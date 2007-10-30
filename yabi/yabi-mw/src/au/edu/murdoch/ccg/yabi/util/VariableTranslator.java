package au.edu.murdoch.ccg.yabi.util;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;

import java.util.*;

import java.util.logging.Logger;

public class VariableTranslator {

    private String separatorRegex = "\\.";
    private String separator = ".";
    
    private static Logger logger = Logger.getLogger( AppDetails.getAppString() + "." + VariableTranslator.class.getName());

    //TODO extend so it can be used without an ExecutionContext, but a variable map and a node name
    //retrieves only the variables that fall within the current node's namespace, split into 'input' and 'output' branches of a hashmap
    public Map getVariableMap(ExecutionContext ctx) {
        HashMap relevantVars = new HashMap();
        HashMap inputVars = new HashMap();
        HashMap outputVars = new HashMap();

        String checkNodeStatus = "";

        //as there is no easy way to get all variables from an ExecutionContext, we use the following convoluted method
        Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
        if (vars != null) {
            Iterator iter = vars.keySet().iterator();
            while (iter.hasNext()) {
                String key = (String) iter.next();
                try {
                    String[] splitName = key.split( separatorRegex );

                    if ( (splitName.length > 2) && (splitName[0].compareTo(getNodeName(ctx)) == 0) ) {
                        //if the variable starts with the current node name then it is one of our variables
                        if ( splitName[1].compareTo("input") == 0 ) {
                            inputVars.put(splitName[2], vars.get(key));
                        }
                        if ( splitName[1].compareTo("output") == 0 ) {
                            outputVars.put(splitName[2], vars.get(key));
                        }
                    }

                    //special case for check node completion status (to detect if we are re-running a node for some reason)
                    if (key.compareTo(getCheckNodeName(ctx) + ".output.jobStatus") == 0) {
                        checkNodeStatus = (String)vars.get(key);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

        //merge vars into a two layer hashmap
        relevantVars.put("input", inputVars);
        relevantVars.put("output", outputVars);
        relevantVars.put("checkStatus", checkNodeStatus);

        return relevantVars;
    }

    //clears all the output variables that fall within the current node's namespace
    //useful when re-running a node that failed at the Submit stage. If it fails at the far end of the Check stage then we may have issues
    //returns the same data structures as getNodeVariableMap so its outputs can be used instead. This is because jbpm doesn't save the
    //variable changes until the end of the context. so these changes are considered transient until then and any 'gets' ignore these changes
    public Map clearNodeOutputMap(ExecutionContext ctx) {
        HashMap relevantVars = new HashMap();
        HashMap inputVars = new HashMap();
        HashMap outputVars = new HashMap();

        String checkNodeStatus = "";

        //as there is no easy way to get all variables from an ExecutionContext, we use the following convoluted method
        Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
        List deleteKeys = new ArrayList();
        if (vars != null) {
            Iterator iter = vars.keySet().iterator();
            while (iter.hasNext()) {
                String key = (String) iter.next();
                try {
                    String[] splitName = key.split( separatorRegex );
                        
                    if ( (splitName.length > 2) && 
                         (splitName[0].compareTo(getNodeName(ctx)) == 0) 
                        ) {
                        //if the variable starts with the current node name then it is one of our variables
                        if ( splitName[1].compareTo("input") == 0 ) {
                            inputVars.put(splitName[2], vars.get(key));
                        }
                        if ( splitName[1].compareTo("output") == 0 ) {
                            deleteKeys.add(key);
                            //System.out.println("[VarTranslator] marked for deletion = "+key);
                        }
                    }

                    //reset the input.jobId for the check-node
                    if ( (splitName.length > 2) &&
                         (key.compareTo(getCheckNodeName(ctx) + ".input.jobId") == 0)
                        ) {
                        ctx.setVariable(key, "derived("+getNodeName(ctx)+".output.jobId)");
                    }
                        
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

        Iterator deleterator = deleteKeys.iterator();
        while (deleterator.hasNext()) {
            String key = (String) deleterator.next();
            //System.out.println("[VarTranslator] delete = "+key);
            ctx.setVariable(key, "");
            ctx.getProcessInstance().getContextInstance().deleteVariable(key);
        }
 
        //merge vars into a two layer hashmap
        relevantVars.put("input", inputVars);
        relevantVars.put("output", outputVars);
        relevantVars.put("checkStatus", checkNodeStatus);

        return relevantVars;
       
    }

    //reformat context variables for a process instance into a map of node names, each containing a Map of variables
    public Map getVariablesByNode(ProcessInstance pi) {
        Map pivars = pi.getContextInstance().getVariables();
        Map nodes = new HashMap();
        
        Iterator iter = pivars.keySet().iterator();
        while (iter.hasNext()) {
            //each item is a variable. we need to reparse the node, whether it is an input or output variable, and the varname
            String key = (String) iter.next();
            try {
                String[] splitName = key.split( separatorRegex );

                HashMap inputVars = new HashMap();
                HashMap outputVars = new HashMap();

                if (splitName.length > 2) {

                    //fetch node variable map for this node, or create it if it doesn't exist
                    Map nodeVars = (Map) nodes.get(splitName[0]);
                    if (nodeVars == null) {
                        nodeVars = new HashMap();
                        nodeVars.put("input", inputVars);
                        nodeVars.put("output", outputVars);
                        nodes.put(splitName[0], nodeVars);
                    } else { //otherwise set convenience maps for inpu/output vars
                        inputVars = (HashMap) nodeVars.get("input");
                        outputVars = (HashMap) nodeVars.get("output");
                    }

                    if ( splitName[1].compareTo("input") == 0 ) {
                        inputVars.put(splitName[2], pivars.get(key));
                    }
                    if ( splitName[1].compareTo("output") == 0 ) {
                        outputVars.put(splitName[2], pivars.get(key));
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
 
        }

        return nodes;
        
    }

    //saves the variable 'variableName' as 'nodeName.output.variableName' and searches for substitutions of this
    //variable in the whole namespace
    //this is done by looking for variables that follow the naming schema
    // c.input.filename = derived(b.output.xreffile)
    //will look up the value b.output.xreffile
    //and set c.input.filename to the value of b.output.xreffile 
    public void saveVariable(ExecutionContext ctx, String variableName, Object variableValue) {
        String fullVarName = getNodeName(ctx) + separator + "output" + separator + variableName;

        //first, save the variable as an output variable
        ctx.setVariable( fullVarName, variableValue );

        this.propagateVariable(ctx, fullVarName, variableValue);
    }

    public void updateLastNodeMarker(ExecutionContext ctx) {
        ctx.setVariable( "lastNode", getNodeName(ctx).replaceAll("-check", "") );
    }

    public String getLastNodeMarker(ExecutionContext ctx) {
        if ( ctx.getVariable( "lastNode" ) != null ) {
            return (String) ctx.getVariable( "lastNode" );
        } else {
            return "";
        }
    }

    //to be reused for globals and node variables
    public void propagateVariable(ExecutionContext ctx, String fullVariableName, Object variableValue) {
        //define a string that is what the 'derived' string would look like
        String derivedString = "derived("+fullVariableName+")";
                    
        List substitutionKeys = new ArrayList();
        //search for substitutions of this variable in the full context variable map
        Iterator iter = ctx.getContextInstance().getVariables().entrySet().iterator();
        while (iter.hasNext()) {
            Map.Entry entry = (Map.Entry) iter.next();
                        
            if ( ((String) entry.getValue()).indexOf( derivedString ) != -1 ) {
                substitutionKeys.add((String)entry.getKey());
            }
        }           
                        
        iter = substitutionKeys.iterator();
        derivedString = "derived\\("+fullVariableName+"\\)";
        while (iter.hasNext()) {
            String key = (String) iter.next();
            String currentValue = (String) ctx.getContextInstance().getVariable(key);
            String replacedValue = currentValue.replaceAll( derivedString, (String)variableValue );

            ctx.getContextInstance().setVariable( key , replacedValue );
            //System.out.println("set ["+key+"] = ["+replacedValue+"]");
        }
    }

    public String getProcessVariable(ExecutionContext ctx, String key) {
        return (String) ctx.getContextInstance().getVariable(key);
    }

    //convenience function for getting the current node name
    protected String getNodeName(ExecutionContext ctx) {
        return ctx.getNode().getFullyQualifiedName();
    }

    protected String getCheckNodeName(ExecutionContext ctx) {
        return getNodeName(ctx) + "-check";
    }

}
