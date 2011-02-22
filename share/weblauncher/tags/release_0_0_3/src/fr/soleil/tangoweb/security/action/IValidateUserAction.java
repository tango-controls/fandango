package fr.soleil.tangoweb.security.action;

public interface IValidateUserAction {

	public abstract boolean validateUser(String strLogin, String strPassword);

}