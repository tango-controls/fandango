package fr.soleil.tangoweb;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.CookieHandler;
import java.net.URL;

import fr.esrf.TangoApi.Connection;
import fr.esrf.TangoApi.DAOImplUtil;
import fr.esrf.webapi.WebServerClientUtil;
import fr.soleil.tangoweb.security.action.LoginAction;
import fr.soleil.util.serialized.IWebServerClient;
import fr.soleil.util.serialized.WebServerClient;
import fr.soleil.util.serialized.WebServerClientPool;

/**
 * WebLauncher method launch the selected application after load specified web classes
 * @author BARBA-ROSSA
 *
 */
public class WebLauncher {

	/**
	 * args[0] : Web Server URL
	 * args[1] : Application class name to launch. These class must have a main() method
	 * args[2] : Display authentication window when window opened : true / false. 
	 * If value equal to false no authentication will be display in when lauching application but the web server could forced to open one.
	 * args[3..n] : Parameter to send to the application launched by WebLauncher
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		
		CookieHandler.setDefault(null);
		
		
		// before launching an application
		// we call the authentication service
		LoginAction loginAction = new LoginAction();
		
		// we get the url of the server
		if(args.length > 1)
		{
			try
			{
				// we get the new url of the web server 
				String strUrl = args[0];
				IWebServerClient defaultWebServerClient = new WebServerClientPool(strUrl);
				WebServerClientUtil.setDefaultClient(defaultWebServerClient);
			}
			catch(Exception e)
			{
				e.printStackTrace();
			}
		}
		
		// It's the default login action
		WebServerClientUtil.getDefaultClient().setM_iLoginAction(loginAction);
		WebServerClientUtil.setIDAOImplUtil(new DAOImplUtil()); // util used to get the DAOImpl
		// we call the authenticate dialog
		//loginAction.authenticateUser();
		
		// We get the parameter, we use in the webLauncher only the first. Other are transmitted to the application called. 
		String[] aParam = new String[]{};
		if(args.length>3)
		{
			aParam = new String[args.length-3];
			for(int i = 3;i<args.length;i++)
			{
				aParam[i-3] = args[i];
			}
		}

		// we put the application name
		WebServerClientUtil.getDefaultClient().setApplication(args[1]);
		
		// if we need to authenticate user  
		// we open the login
		if("true".trim().equalsIgnoreCase(args[2]))
			loginAction.authenticateUser();
		
		
		// We check if the server is available
		pingServer();
		
		System.setProperty("TANGO_HOST", "TANGO_WEB_SERVER::80");
		if(args.length < 2)
		{
			WebServerClientUtil.getDefaultClient().setApplication("machinestatus");
		}
		else
		{
			// we set the application name
			WebServerClientUtil.getDefaultClient().setApplication(args[1]);
			invokeClass(args[1], aParam);
		}
	}

	private static void pingServer()
	{
		try 
		{
		System.out.println("Before launching the application : access to the server ");
		Connection connection = new Connection();
		int idlVersion =connection.get_idl_version();
		System.out.println("Ping server idlVersion : " + idlVersion);
		System.out.println("Ping server name : " + connection.get_name());
		}catch(Exception e)
		{
			e.printStackTrace();
		}
	}
	
	/**
	 * Launch main method of the class in parameter
	 * @param className
	 * @param aParam
	 * @throws Exception
	 */
	private static void invokeClass(String className, String[] aParam) throws Exception
	{
	    try {

	        // we get the class definition object
	        Class c = Class.forName(className);

	        // we get the method definition
	        Method m = c.getMethod("main", new Class[]{aParam.getClass()});
	        
	        // We execute the method.
	        m.invoke(null, new Object[]{aParam});
	        
	      } catch (ClassNotFoundException e) {
	        System.out.println("Class.forName(  ) can't find the class");
	        throw e;
	      } catch (NoSuchMethodException e2) {
	        System.out.println("method doesn't exist");
	        throw e2;
	      } catch (IllegalAccessException e3) {
	        System.out.println("no permission to invoke that method");
	        throw e3;
	      } catch (InvocationTargetException e) {
	        System.out.println("an exception ocurred while invoking that method");
	        System.out.println("Method threw an: " + e.getTargetException());
	        
	        // if we have a instanceof Exception we throw it else we throw the invocation exception
	        if(e.getTargetException() instanceof Exception)
	        	throw (Exception)e.getTargetException();
	        else
	        	throw e;
	      }		
	}	
	
}
