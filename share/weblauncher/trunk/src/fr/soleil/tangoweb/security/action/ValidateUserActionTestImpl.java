package fr.soleil.tangoweb.security.action;

import fr.esrf.webapi.WebServerClientUtil;
import fr.soleil.util.serialized.WebReflectRequest;
import fr.soleil.util.serialized.WebRequest;
import fr.soleil.util.serialized.WebResponse;

/**
 * Contains services to validate the user information
 * @author BARBA-ROSSA
 *
 */
public class ValidateUserActionTestImpl implements IValidateUserAction {

	/* (non-Javadoc)
	 * @see fr.soleil.tangoweb.security.action.IValidateUserAction#validateUser(java.lang.String, java.lang.String)
	 */
	public boolean validateUser(String strLogin, String strPassword)
	{
		if(strLogin == null)
			return false;
		if(strPassword == null)
			return false;
		if("".equalsIgnoreCase(strLogin.trim()))
			return false;
		if("".equalsIgnoreCase(strPassword.trim()))
			return false;	
		
		// for the moment we just put this control
		try
		{
			WebRequest request = new WebRequest();
			Object[] classParam = new Object[]{strLogin,strPassword};
			WebReflectRequest reflectRequest = new WebReflectRequest("Security.authenticate", classParam, null, null, null);
			request.setArguments(new Object[]{reflectRequest});
			WebResponse response = WebServerClientUtil.getDefaultClient().getObject(request);
			Boolean authenticated = (Boolean)response.getResult()[0];
			if(authenticated.booleanValue())
				return true;
			else
				return false;
		}
		catch(Exception e)
		{
			e.printStackTrace();
			return false;
		}
	}
}
