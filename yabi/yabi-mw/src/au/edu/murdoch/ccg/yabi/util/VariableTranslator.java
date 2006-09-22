package au.edu.murdoch.ccg.yabi.util;

import org.jbpm.graph.def.*;
import org.jbpm.graph.exe.*;
import org.jbpm.*;

import java.util.*;

public class VariableTranslator {

    private String separatorRegex = "\\.";
    private String separator = ".";

    //TODO extend so it can be used without an ExecutionContext, but a variable map and a node name
    //retrieves only the variables that fall within the current node's namespace, split into 'input' and 'output' branches of a hashmap
    public Map getVariableMap(ExecutionContext ctx) {
        HashMap relevantVars = new HashMap();
        HashMap inputVars = new HashMap();
        HashMap outputVars = new HashMap();

        //as there is no easy way to get all variables from an ExecutionContext, we use the following convoluted method
        Map vars = ctx.getProcessInstance().getContextInstance().getVariables();
        Iterator iter = vars.keySet().iterator();
        while (iter.hasNext()) {
            String key = (String) iter.next();
            try {
                String[] splitName = key.split( separatorRegex );

                if ( (splitName.length > 1) && (splitName[0].compareTo(getNodeName(ctx)) == 0) ) {
                    //if the variable starts with the current node name then it is one of our variables
                    if ( splitName[1].compareTo("input") == 0 ) {
                        inputVars.put(splitName[2], vars.get(key));
                    }
                    if ( splitName[1].compareTo("output") == 0 ) {
                        outputVars.put(splitName[2], vars.get(key));
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        //merge vars into a two layer hashmap
        relevantVars.put("input", inputVars);
        relevantVars.put("output", outputVars);

        return relevantVars;
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

        //TODO search for substitutions of this variable in the full context variable map
    }

    //convenience function for getting the current node name
    protected String getNodeName(ExecutionContext ctx) {
        return ctx.getNode().getFullyQualifiedName();
    }

}
