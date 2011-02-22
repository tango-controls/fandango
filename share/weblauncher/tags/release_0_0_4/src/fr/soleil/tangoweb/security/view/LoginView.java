package fr.soleil.tangoweb.security.view;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;

import javax.swing.InputMap;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;
import javax.swing.KeyStroke;
import javax.swing.SpringLayout;

import fr.soleil.tangoweb.security.action.IValidateUserAction;
import fr.soleil.util.swing.SpringUtilities;

/**
 * First version of the login window
 * @author BARBA-ROSSA
 *
 */
public class LoginView {

	private JDialog m_dialog = null;
	private JPanel m_pnlMain = null;
	
	private JPanel m_pnlError = null;
	private JLabel m_lblError = null;
	private JPanel m_pnlLogin = null;	
	private JPanel m_pnlBtn  = null;
	
	private JTextField m_txtLogin = null;
	private JPasswordField m_txtPassword = null;
	private JButton m_btvalidate = null;
	
	private IValidateUserAction m_validateAction = null;
	
	private boolean m_bIsValid = false;
	
	public LoginView(JFrame frame, IValidateUserAction validateAction, String strMsgError)
	{
		init(frame, validateAction, strMsgError);
	}
	
	public void init(JFrame frame, IValidateUserAction validateAction, String strMsgError)
	{
		
		m_validateAction = validateAction;
		
		m_dialog = new JDialog(frame, true);
		m_dialog.setSize(new Dimension(350,220));
		m_dialog.setResizable(false);
		m_dialog.setTitle("Authentication");
		m_dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
		m_dialog.addWindowListener(new WindowListener(){

			public void windowClosed(WindowEvent e) {
				if(!m_bIsValid)
					System.exit(1);				
			}

			public void windowClosing(WindowEvent e) {
				if(!m_bIsValid)
					System.exit(1);				
			}

			public void windowActivated(WindowEvent e) {}
			public void windowDeactivated(WindowEvent e) {}
			public void windowDeiconified(WindowEvent e) {}
			public void windowIconified(WindowEvent e) {}
			public void windowOpened(WindowEvent e) {}
			});
		m_pnlMain = new JPanel();
		m_pnlMain.setLayout(new SpringLayout());
		
		// add title
		createPnlTitle();
		
		// add the error panel
		m_pnlError = new JPanel(new FlowLayout(FlowLayout.CENTER));
		m_pnlError.setPreferredSize(new Dimension(350,20));
		m_lblError = new JLabel(strMsgError);
		m_lblError.setForeground(Color.RED);
		m_pnlError.add(m_lblError);
		m_pnlMain.add(m_pnlError);
		
		// add panel with login and password textfield
		createPnlLogin();
		m_pnlMain.add(m_pnlLogin);
		SpringUtilities.makeCompactGrid(m_pnlLogin, 2, 2, 0, 0, 10, 5);
		
		// add action button panel
		createPnlButton();
		m_pnlMain.add(m_pnlBtn);
		SpringUtilities.makeCompactGrid(m_pnlMain, 4, 1, 5, 5, 5, 5);
		
		m_dialog.setContentPane(m_pnlMain);
	}
	
	public void setVisible(boolean isVisible)
	{
		m_bIsValid = false;
		m_dialog.setLocationRelativeTo(null);
		m_pnlMain.setVisible(isVisible);
		m_dialog.setVisible(isVisible);
	}
	
	private void createPnlTitle()
	{
		JPanel pnlTitle = new JPanel(new SpringLayout());
		JLabel title = new JLabel("Login");
		JLabel label = new JLabel("Please enter your username and your password.");
		Font newFont = title.getFont().deriveFont((float) 14.0);
		title.setFont(newFont);
		pnlTitle.add(title);
		pnlTitle.add(label);
		SpringUtilities.makeCompactGrid(pnlTitle, 2, 1, 5, 5, 5, 5);
		m_pnlMain.add(pnlTitle);
	}
	
	private void createPnlLogin()
	{
		m_pnlLogin = new JPanel();
		m_pnlLogin.setLayout(new SpringLayout());
		m_pnlLogin.add(new JLabel("Username"));
		m_txtLogin = new JTextField(20);
		m_txtLogin.setPreferredSize(new Dimension(120,20));
		m_txtLogin.setMaximumSize(new Dimension(1900,20));
		m_pnlLogin.add(m_txtLogin);
		m_pnlLogin.add(new JLabel("Password"));
		m_txtPassword = new JPasswordField(20);
		m_txtPassword.setPreferredSize(new Dimension(120,20));
		m_txtPassword.setMaximumSize(new Dimension(1900,20));
		m_txtPassword.addKeyListener(new KeyListener()
		{

			public void keyPressed(KeyEvent e)
			{
				if(e.getKeyCode() == KeyEvent.VK_ENTER)
				{
					validateUser();
				}
			}
			public void keyReleased(KeyEvent e)
			{
			}

			public void keyTyped(KeyEvent e)
			{
			}
			
		}
		);		
		m_pnlLogin.add(m_txtPassword);		
	}
	
	private void createPnlButton()
	{
		FlowLayout layout = new FlowLayout(FlowLayout.RIGHT);
		m_pnlBtn = new JPanel(layout);
		m_pnlBtn.setPreferredSize(new Dimension(350,32));
		m_pnlBtn.setMaximumSize(new Dimension(350,33));
		m_btvalidate = new JButton("OK");
		m_btvalidate.addActionListener(new ActionListener(){

			public void actionPerformed(ActionEvent e) {
				validateUser();
			}
		});
		m_pnlBtn.add(m_btvalidate);

		JButton btcancel = new JButton("Cancel");
		// We link the key event [ESCAPE] to the exit dialog 
		InputMap cancelInputMap = btcancel.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW);
		KeyStroke cancelStroke = KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0);
		cancelInputMap.put(cancelStroke, "cancelAction");
		btcancel.addActionListener(new ActionListener(){

			public void actionPerformed(ActionEvent e) {
				System.exit(1);
			}
		});
		
		m_pnlBtn.add(btcancel);
		
	} 
	
	private void validateUser()
	{
		String strLogin = m_txtLogin.getText();
		String strPassword = m_txtPassword.getText();
		boolean isValid = m_validateAction.validateUser(strLogin, strPassword);
		if(isValid)
		{
			m_bIsValid = true;
			m_dialog.dispose();			
		}
		else
		{
			// temp add a simple error message
			m_bIsValid = false;
			m_lblError.setText("Error user invalid");
			SpringUtilities.makeCompactGrid(m_pnlMain, 4, 1, 5, 5, 5, 5);
		}
	}
}
