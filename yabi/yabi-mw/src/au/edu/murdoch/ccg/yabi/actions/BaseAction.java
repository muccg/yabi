package au.edu.murdoch.ccg.yabi.actions;

import au.edu.murdoch.ccg.yabi.util.*;

import org.jbpm.graph.def.ActionHandler;
import org.jbpm.graph.exe.ExecutionContext;
import java.util.*;

public abstract class BaseAction implements ActionHandler {

    //define a variable translator for manipulating the flat context variable namespace
    protected VariableTranslator varTranslator = new VariableTranslator();

    //convenience function for getting the current node name
    protected String getNodeName(ExecutionContext ctx) {
        return ctx.getNode().getFullyQualifiedName();
    }

}
