package au.edu.murdoch.ccg.yabi.objects;

public class User {

    //this class will encapsulate all the info we need to know about a user
    //packaging up all their auth details for various services and storing other details
    
    private String username;
    
    /****************************************************************************/
    
    public User(String username) {
        this.username = username;
    }
    
    /****************************************************************************/

    public String getUsername() { return this.username; }
    public void setUsername(String username) { this.username = username; }

}
