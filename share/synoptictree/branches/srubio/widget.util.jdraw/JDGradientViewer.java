/** A JDGradient editor */
package fr.esrf.tangoatk.widget.util.jdraw;

import javax.swing.*;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.event.MouseEvent;
import java.awt.*;

class JDGradientViewer extends JComponent implements MouseListener,MouseMotionListener {

  private Cursor moveCursor = Cursor.getPredefinedCursor(Cursor.MOVE_CURSOR);
  private Cursor defaultCursor = Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR);
  private static final double arrowLgth=50.0;
  private static final Color transBlue=new Color(0,255,0,196);

  private GradientPaint gradient = null;
  private double amp;
  private double vx;
  private double vy;
  private int xc=0;
  private int yc=0;
  private int dragMode=0;
  private double offset;

  public JDGradientViewer() {
    addMouseListener(this);
    addMouseMotionListener(this);
  }

  public void setGradient(float x1, float y1, Color color1, float x2, float y2, Color color2, boolean cyclic) {
    gradient = new GradientPaint(x1,y1,color1,x2,y2,color2,cyclic);
    vx = x2-x1;
    vy = y2-y1;
    amp = Math.sqrt( vx*vx + vy*vy );
    vx = vx*arrowLgth / amp;
    vy = vy*arrowLgth / amp;
    offset = Math.sqrt( x1*x1 + y1*y1 );
    repaint();
  }

  public float getX1() {
    return (float)gradient.getPoint1().getX();
  }
  public float getY1() {
    return (float)gradient.getPoint1().getY();
  }
  public float getX2() {
    return (float)gradient.getPoint2().getX();
  }
  public float getY2() {
    return (float)gradient.getPoint2().getY();
  }

  public Color getColor1() {
    return gradient.getColor1();
  }

  public void setColor1(Color c1) {
    setGradient((float) gradient.getPoint1().getX(), (float) gradient.getPoint1().getY(),
            c1,
            (float) gradient.getPoint2().getX(), (float) gradient.getPoint2().getY(),
            gradient.getColor2(),
            gradient.isCyclic());
  }

  public Color getColor2() {
    return gradient.getColor2();
  }

  public void setColor2(Color c2) {
    setGradient((float) gradient.getPoint1().getX(), (float) gradient.getPoint1().getY(),
            gradient.getColor1(),
            (float) gradient.getPoint2().getX(), (float) gradient.getPoint2().getY(),
            c2,
            gradient.isCyclic());
  }

  public boolean isCyclic() {
    return gradient.isCyclic();
  }

  public void setCyclic(boolean b) {
    setGradient((float) gradient.getPoint1().getX(), (float) gradient.getPoint1().getY(),
            gradient.getColor1(),
            (float) gradient.getPoint2().getX(), (float) gradient.getPoint2().getY(),
            gradient.getColor2(),
            b);
  }

  public int getAmplitupe() {
    return (int)(amp+0.5);
  }

  public void setAmplitute(int a) {
    double r = (double)a/amp;
    double nx2 = gradient.getPoint2().getX() - gradient.getPoint1().getX();
    double ny2 = gradient.getPoint2().getY() - gradient.getPoint1().getY();

    setGradient((float) gradient.getPoint1().getX(),
                (float) gradient.getPoint1().getY(),
                gradient.getColor1(),
                (float)( gradient.getPoint1().getX() + nx2 * r),
                (float)( gradient.getPoint1().getY() + ny2 * r),
                gradient.getColor2(),
                gradient.isCyclic());
  }

  public int getOffset() {
    return (int)(offset+0.5);
  }

  public void setOffset(int a) {
    double nOffset = (double)a - offset;
    double r = nOffset / arrowLgth;
    float tx = (float)(vx*r);
    float ty = (float)(vy*r);
    setGradient((float) gradient.getPoint1().getX()+tx, (float) gradient.getPoint1().getY()+ty,
            gradient.getColor1(),
            (float) gradient.getPoint2().getX()+tx, (float) gradient.getPoint2().getY()+ty,
            gradient.getColor2(),
            gradient.isCyclic());
  }

  public void paint(Graphics g) {
    if( gradient!=null ) {

      Dimension d=getSize();
      xc = d.width/2;
      yc = d.height/2;

      // Paint the gradient
      g.translate(xc,yc);
      ((Graphics2D)g).setPaint(gradient);
      g.fillRect(-xc,-yc,d.width,d.height);
      g.translate(-xc,-yc);

      // Paint the radial slider
      g.setColor(transBlue);
      g.fillRect(xc-2,yc-2,5,5);
      g.drawLine(xc,yc,xc+(int)vx,yc+(int)vy);
      g.drawRect(xc+(int)vx-3,yc+(int)vy-3,6,6);
      g.drawOval(xc-(int)arrowLgth,yc-(int)arrowLgth,(int)(2.0*arrowLgth),(int)(2.0*arrowLgth));

    }
    paintBorder(g);
  }


  public void mousePressed(MouseEvent e) {
    if(isInside(e))
      dragMode = 1;
    else
      dragMode = 0;
  }

  public void mouseReleased(MouseEvent e) {
    dragMode=0;
  }

  public void mouseDragged(MouseEvent e) {

    if(dragMode==1) {

      // Compute normals
      double nx = e.getX()-xc;
      double ny = e.getY()-yc;
      double nn = Math.sqrt(nx*nx+ny*ny);

      double x1 = gradient.getPoint1().getX();
      double y1 = gradient.getPoint1().getY();
      double n1 = Math.sqrt(x1*x1+y1*y1)/nn;

      double x2 = gradient.getPoint2().getX();
      double y2 = gradient.getPoint2().getY();
      double n2 = Math.sqrt(x2*x2+y2*y2)/nn;

      if (nn > 5.0) {
        setGradient(
                (float) (nx*n1),
                (float) (ny*n1),
                gradient.getColor1(),
                (float) (nx*n2),
                (float) (ny*n2),
                gradient.getColor2(),
                gradient.isCyclic());

      }

    }

  }

  public void mouseMoved(MouseEvent e) {
    if(isInside(e))
      setCursor(moveCursor);
    else
      setCursor(defaultCursor);
  }

  private boolean isInside(MouseEvent e) {
    int px = xc+(int)vx - e.getX();
    int py = yc+(int)vy - e.getY();
    return (px>-5 && px<5 && py>-5 && py<5);
  }


  public void mouseEntered(MouseEvent e) {}
  public void mouseExited(MouseEvent e) {}
  public void mouseClicked(MouseEvent e) {}

}
