package fr.soleil.tangoweb.security.action;

import javax.swing.JFrame;


import fr.soleil.tangoweb.security.view.LoginView;
import fr.soleil.util.serialized.ILoginAction;

public class LoginAction implements ILoginAction {

	/* (non-Javadoc)
	 * @see fr.soleil.tangoweb.security.action.ILoginAction#authenticateUser()
	 */
	public void authenticateUser()
	{
		  LoginView prompt = new LoginView(new JFrame(), new ValidateUserActionTestImpl(),"");
		  prompt.setVisible(true);
	}
	
}
