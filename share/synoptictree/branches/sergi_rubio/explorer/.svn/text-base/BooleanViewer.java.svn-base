package explorer;

import java.awt.Color;
import javax.swing.ImageIcon;
import javax.swing.JCheckBox;

/**
 * A <code>JCheckBox</code> compatible viewer that looks like a double LED. It
 * is usefull to represent a boolean scalar attribute, because it can be
 * parametered with a <code>Boolean</code> value. If this value is true, then
 * the green LED will light up. If it is false, this is the LED led which lights
 * up. If it is null, no LED lights up.
 * 
 * @author GIRARDOT
 */
public class BooleanViewer extends JCheckBox
{

    private final static ImageIcon trueIcon = new ImageIcon(Main.class.getResource("ui/true.gif"));
    private final static ImageIcon falseIcon = new ImageIcon(Main.class.getResource("ui/false.gif"));
    private final static ImageIcon offIcon = new ImageIcon(Main.class.getResource("ui/double_off.gif"));

    /**
     * Constructor
     *
     * @param value a Boolean to select/unselect the checkbox
     */
    public BooleanViewer (Boolean value)
    {
        super( (value == null)? "No Data":value.toString() );
        setOpaque(true);
        setBackground(Color.WHITE);
        setIcon(falseIcon);
        setPressedIcon(offIcon);
        setSelectedIcon(trueIcon);
        setSelected( value );
        repaint();
    }

    /**
     * Changes the appearence (selected, not selected) with a Boolean value
     * 
     * @param value
     *            the Boolean value
     */
    public void setSelected(Boolean value)
    {
        if (value == null)
        {
            setSelected(false);
            setIcon(offIcon);
            repaint();
        }
        else
        {
            setIcon(falseIcon);
            setSelected(value.booleanValue());
            repaint();
        }
    }

    public void setText(String text)
    {
        if ("true".equalsIgnoreCase(text.trim()))
        {
            super.setText("true");
            setSelected(new Boolean(true));
        }
        else if ("false".equalsIgnoreCase(text.trim()))
        {
            super.setText("false");
            setSelected(new Boolean(false));
        }
        else
        {
            super.setText("No Data");
            setSelected(null);
        }
    }

}
