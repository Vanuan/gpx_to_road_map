/*
Frechet-based map construction 1.0
Copyright 2013 Mahmuda Ahmed and Carola Wenk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

------------------------------------------------------------------------

This software is based on the following article. Please cite this
article when using this code as part of a research publication:

Mahmuda Ahmed and Carola Wenk, "Constructing Street Networks from GPS
Trajectories", European Symposium on Algorithms (ESA): 60-71,
Ljubljana, Slovenia, 2012

------------------------------------------------------------------------

Author: Mahmuda Ahmed
Filename: Line.java
 */
package mapConstruction;


public class Line {
 private Vertex p1;
 private Vertex p2; 
 double xdiff,ydiff;
 double c,m,theta;
 
 public Line(Vertex p1, Vertex p2)
 {
  this.p1 = p1;
  this.p2 = p2;
  this.xdiff = p2.x - p1.x;
  this.ydiff = p2.y - p1.y;
  this.m = (p2.y-p1.y)/(p2.x-p1.x);
  this.c = ((p1.y+p2.y) - m*(p1.x+p2.x))/2; 
  if(this.xdiff!=0)this.theta = Math.atan(this.m);
  else if( this.ydiff > 0 ) this.theta = Math.PI/2;
  else this.theta = -Math.PI/2;
  
 } 
 
 public String toString()
 {
  return "["+this.p1.x+" "+this.p1.y+"; "+this.p2.x+" "+this.p2.y+"]";
 }
 double detr=-10, b_t, a_t, c_t;
 public double[] pIntersection(Vertex p, double eps)
 {
  
  double t[] = new double[2];
  /* Line 1: x1+(x2-x1)*t = x; x1+xdiff*t = x 
    y1+(y2-y1)*t = y; y1+ydiff*t = y
    
    (x-a)^2+(y-b)^2=eps^2
    (x1+xdiff*t-a)^2+(y1+ydiff*t-b)^2=eps^2
    (xdiff^2+ydiff^2)t^2 + (2(x1-a)xdiff+2(y1-b)ydiff)t + (x1-a)^2+(y1-b)^2-eps^2=0
    
    t = (-(2(x1-a)xdiff+2(y1-b)ydiff)) +- sqrt((2(x1-a)xdiff+2(y1-b)ydiff))^2 - 4(xdiff^2+ydiff^2)(x1^2+y1^2-eps^2)))/(2*(xdiff^2+ydiff^2))
    
    */
  
  double b_t = 2*((p1.x-p.x)*this.xdiff+(p1.y-p.y)*this.ydiff);
  double c_t = (p1.x-p.x)*(p1.x-p.x) + (p1.y-p.y)*(p1.y-p.y) - eps*eps;
  double a_t = this.xdiff*this.xdiff + this.ydiff*this.ydiff;
  this.b_t = b_t;
  this.a_t = a_t;
  this.c_t = c_t;
  
  if(a_t == 0){
  /* System.out.println("a_t="+a_t+",b_t="+b_t+", c_t="+c_t);
   System.out.println("disc="+ (b_t*b_t - 4*a_t*c_t));
   System.out.println(p1.toString()+p2.toString());*/
   return null;
  }
  
  double determinent = b_t*b_t - 4*a_t*c_t;
  detr = determinent;
  if(determinent>=0){
   t[1] = (-b_t + Math.sqrt(determinent))/(2*a_t);
   t[0] = (-b_t - Math.sqrt(determinent))/(2*a_t);
  }
  /*else if(determinent>=-50)
  {
   t[1] = (-b_t + Math.sqrt(0))/(2*a_t);
   t[0] = (-b_t - Math.sqrt(0))/(2*a_t);
  }*/
  else{
   //System.out.println("I am retunrd from here "+detr +" "+ Math.sqrt(Math.abs(detr))/(2*a_t));
   return null;
  }
  return t;
 }
 
 public double[] pIntersection2(Vertex p, double eps)
 {
  
  double t[] = new double[2];
  /* Line 1: x1+(x2-x1)*t = x; x1+xdiff*t = x 
    y1+(y2-y1)*t = y; y1+ydiff*t = y
    
    (x-a)^2+(y-b)^2=eps^2
    (x1+xdiff*t-a)^2+(y1+ydiff*t-b)^2=eps^2
    (xdiff^2+ydiff^2)t^2 + (2(x1-a)xdiff+2(y1-b)ydiff)t + (x1-a)^2+(y1-b)^2-eps^2=0
    
    t = (-(2(x1-a)xdiff+2(y1-b)ydiff)) +- sqrt((2(x1-a)xdiff+2(y1-b)ydiff))^2 - 4(xdiff^2+ydiff^2)(x1^2+y1^2-eps^2)))/(2*(xdiff^2+ydiff^2))
    
    */
  
  
  double a_t = this.xdiff*this.xdiff + this.ydiff*this.ydiff;
  
  
  if(a_t == 0){
   System.out.println("a_t="+a_t+",b_t="+b_t+", c_t="+c_t);
   System.out.println("disc="+ (b_t*b_t - 4*a_t*c_t));
   System.out.println(p1.toString()+p2.toString());
   return null;
  }
  double b_t = 2*((p1.x-p.x)*this.xdiff+(p1.y-p.y)*this.ydiff);
  double c_t = (p1.x-p.x)*(p1.x-p.x) + (p1.y-p.y)*(p1.y-p.y) - eps*eps;
  
  this.b_t = b_t;
  this.a_t = a_t;
  this.c_t = c_t;
  
  double determinent = b_t*b_t - 4*a_t*c_t;
  detr = determinent;
  
  if(determinent>=0){
   t[1] = (-b_t + Math.sqrt(determinent))/(2*a_t);
   t[0] = (-b_t - Math.sqrt(determinent))/(2*a_t);
  }
  else if(Math.sqrt(Math.abs(detr))/(2*a_t)*Math.sqrt(a_t) < 0.03)
  {
   t[1] = (-b_t + Math.sqrt(0))/(2*a_t);
   t[0] = (-b_t - Math.sqrt(0))/(2*a_t);
  }
  else{
   //System.out.println("I am retunrd from here "+detr);
   return null;
  }
  
  double min = Math.min(t[0], t[1]);
  double max = Math.max(t[0], t[1]);
  
  t[0] = min;
  t[1] = max;
  
  return t;
 }
 
 public boolean pIntersection(Edge e, double eps)
 {
  
  
  boolean debug = false, debug2 = false;
  //if(MapConstruction.curveid == 368){debug2 =true;}
  /* Line 1: x1+(x2-x1)*t = x
      y1+(y2-y1)*t = y
   Line 2: y = mx + c
    y1+(y2-y1)*t = (x1+(x2-x1)*t)*m + c
    (y2-y1)*t - (x2-x1)*t*m = x1*m + c- y1
    t = (x1*m + c - y1)/((y2-y1)-(x2-x1)*m)
  */
  //System.out.println("C"+line.getConstant());
  
  
  
   Line vline = e.line;
   //System.out.println(vline.toString());
   
   Line line[] = this.getEpsilonNeiborhood(vline, eps);
   double i1,i2,i3,i4;
   double vstart=-1, vend=-1;
   
   if(Math.abs(this.theta) == Math.abs(line[0].theta))
   {
    //System.out.println(i1+" "+i2);
    
    
    double t[] = this.getTParallel(vline, eps);
    if(t == null) 
    {
     //System.out.println(i1+" "+i2);
     //if(debug2)System.out.println("We are parallel returned false.");
     return false;
    }
    i1 = t[0];
    i2 = t[1];
    i3 = 0;
    i4 = 1;
    if(debug2){
     System.out.println("We are parallel."+this.m+" "+line[0].m+" "+this.theta+" "+line[0].theta);
     System.out.println("eline1: "+e.line.toString());
     System.out.println("this1: "+ this.toString());
    }
   } 
   else { 
   
    
   if(line[0].xdiff == 0 ){
    i1 = this.m*line[0].p1.x+this.c;
    i2 = this.m*line[1].p1.x+this.c;
    
    i3 = (i1-line[0].p1.y)/(line[0].p2.y - line[0].p1.y);
    i4 = (i2-line[1].p1.y)/(line[1].p2.y - line[1].p1.y);
     
    i1 = (i1-this.p1.y)/(this.p2.y - this.p1.y);
    i2 = (i2-this.p1.y)/(this.p2.y - this.p1.y);
   }  
   else if(this.xdiff == 0)
   {
    i1 = line[0].m*this.p1.x+line[0].c;
    i2 = line[1].m*this.p1.x+line[1].c;
    
    i3 = (i1-line[0].p1.y)/(line[0].p2.y - line[0].p1.y);
    i4 = (i2-line[1].p1.y)/(line[1].p2.y - line[1].p1.y);
     
    i1 = (i1-this.p1.y)/(this.p2.y - this.p1.y);
    i2 = (i2-this.p1.y)/(this.p2.y - this.p1.y);
   }
   else
   {
    i1 = -(this.c-line[0].c)/(this.m-line[0].m);
    i2 = -(this.c-line[1].c)/(this.m-line[1].m);
    
    i3 = (i1-line[0].p1.x)/(line[0].p2.x - line[0].p1.x);
    i4 = (i2-line[1].p1.x)/(line[1].p2.x - line[1].p1.x);
     
    i1 = (i1-this.p1.x)/(this.p2.x - this.p1.x);
    i2 = (i2-this.p1.x)/(this.p2.x - this.p1.x);
   }
   
   //System.out.println(this.m+" "+line[0].m);
  
   
  
   //System.out.println(line[0].toString());
   //System.out.println(line[1].toString());
   
   if(line[0].p2.x - line[0].p1.x == 0)
   {
    if(debug)System.out.println("We are weired.");
    return false;
   }
   
   
   
   
   }
    
   double interval1[] = new double[2];
   double interval2[] = new double[2];
   double interval[] = new double[2];
  
   if(debug)System.out.println(i1+" "+i2+" "+i3+" "+i4); 
   
   if( i1 > i2 )
   {
    double temp = i1;
    i1 = i2;
    i2 = temp;
    
    temp = i3;
    i3 = i4;
    i4 = temp;
   }
 
  
  
  interval1 = this.pIntersection(vline.p1, eps);
  //System.out.println("I was called interval 1"); 
  interval2 = this.pIntersection(vline.p2, eps);
  //System.out.println("I was called interval 2"); 
  double min1=0,min2=0,max1=1,max2=1;
  
  if(debug)System.out.println("BCO: "+i1+" "+i2+" "+i3+" "+i4);
  
  //case one
  
  if(interval1 == null && interval2 == null)
  {
   //case one
   if( i1 > 1 || i2 < 0 ) return false;
   //case two
   if( ( i3 > 1 && i4 > 1 ) || ( i3 < 0 && i4 < 0 ) ) return false;
   
   if(i3 >= 0 && i3 <= 1 && i4 >= 0 && i4 <= 1 )
   {
    i1 = Math.max(0, i1);
    i2 = Math.min(1, i2);
   }   
   else
    return false;
  }
  
  //case two
  
  if(debug)System.out.println("ACO: "+i1+" "+i2);
  
  if( interval1 != null )
  {
   
   min1 = Math.min(interval1[0],interval1[1]);
   max1 = Math.max(interval1[0],interval1[1]);
   
   if( (( i3 > 1 && i4 > 1 ) || ( i3 < 0 && i4 < 0 )) && (min1 > 1 || max1 < 0)) return false;
   
   if(debug)System.out.println("min1="+min1+" max1="+max1);
   
   if( i3 < 0 )
   {
    if( min1 <= 1 ) i1 = Math.max(i1, min1);
    if(i1 == min1) vstart = 0;
   }
   
   if( i4 < 0 )
   {
    if( max1 >= 0 ) i2 = Math.min(i2, max1);
    if(i2 == max1) vend = 0;
   }
   
   /*if( i3 <= i4 )
   {
    if( i3 >= 1 || i3 <= 0 )
    {
     if( min1 <= 1 ) i1 = Math.max(i1, min1);
     if(i1 == min1) vstart = 0;
    }
   }
   else if( i3 > i4 )
   {
    if( i4 >= 1 || i4 <= 0 )
    {
     if( max1 >= 0 ) i2 = Math.min(i2, max1);
     if(i2 == max1) vend = 0;
    }
   }*/
   
  }
  if(debug)System.out.println("ACT: "+i1+" "+i2);
  //case three
  if( interval2 != null )
  {
   min2 = Math.min(interval2[0],interval2[1]);
   max2 = Math.max(interval2[0],interval2[1]);
   
   if( (( i3 > 1 && i4 > 1 ) || ( i3 < 0 && i4 < 0 )) && (min2 > 1 || max2 < 0)) return false;
   
   if(debug)System.out.println("min2="+min2+" max2="+max2);

   if( i3 > 1 )
   {
    if( min2 <= 1 )i1 = Math.max(i1, min2);
    if(i1 == min2) vstart = 1;
   }
   
   if( i4 > 1)
   {
    if( max2 >= 0 )i2 = Math.min(i2, max2);
    if(i2 == max2) vend = 1;
   }
   /*if( i3 <= i4 )
   {
    if( i4 >= 1 || i4 <= 0 )
    {
     if( max2 >= 0 )i2 = Math.min(i2, max2);
     if(i2 == max2) vend = 1;
    }
   }
   else if( i3 > i4 )
   {
    if( i3 >= 1 || i3 <= 0 )
    {
     if( min2 <= 1 )i1 = Math.max(i1, min2);
     if(i1 == min2) vstart = 1;
    }
   }*/
  }
  
  if(debug)System.out.println("ACTh: "+i1+" "+i2);
  
  if(interval1 == null && interval2 != null)
  {
   if(i3 >= 0 && i3 <= 1 && i4 >= 0 && i4 <= 1)
   {
    
   }
   else{
    if( i3 >= 0 && i3 <= 1 )
    {
     if( i1 > 1 && min2 > 1 )return false;
     if( i1 < 0 && max2 < 0 )return false;
    }
    if( i4 >= 0 && i4 <= 1 )
    {
     if( i2 > 1 && min2 > 1 )return false;
     if( i2 < 0 && max2 < 0 )return false;
    }
   }
  }
  if(interval1 != null && interval2 == null)
  {
   if(i3 >= 0 && i3 <= 1 && i4 >= 0 && i4 <= 1)
   {
    
   }
   else{
    
    if( i3 >= 0 && i3 <= 1 )
    {
     if( i1 > 1 && min1 > 1 )return false;
     if( i1 < 0 && max1 < 0 )return false;
    }
    if( i4 >= 0 && i4 <= 1 )
    {
     if( i2 > 1 && min1 > 1 )return false;
     if( i2 < 0 && max1 < 0 )return false;
    }
   }
  }
  
 
  
  if( i1 > i2 )
  {
   double temp = i1;
   i1 = i2;
   i2 = temp;
   
   temp = vend;
   vend = vstart;
   vstart = temp;
  }
  //case one
  if( i1 > 1 || i2 < 0 ) return false;
  //case two
  //if( ( i3 > 1 && i4 > 1 ) || ( i3 < 0 && i4 < 0 ) ) return false;
  
  if(Math.max(max1, max2) < 0 || Math.min(min1, min2) > 1 ) return false;
  
  double in1[] = new double[2];
  double in2[] = new double[2];
  try{   
   interval[0] = Math.max(0, i1);
   
   if(vstart == -1)
   {
   
    in1= vline.pIntersection2(this.getVertex(interval[0]), eps);
    if(debug2)System.out.println(MapConstruction.startIndex+" I was called from here 1." + in1);
    if(in1[0]>=0 && in1[0]<=1 && in1[1]>=0 && in1[1]<=1)
     vstart = (in1[0]+in1[1])/2;
    else if(in1[0]>=0 && in1[0]<=1)vstart=in1[0];
    else if(in1[1]>=0 && in1[1]<=1)vstart=in1[1];
    else vstart = 0;
   }
   
   interval[1] = Math.min(1, i2);
   
   if(vend == -1)
   {
   
    in2 = vline.pIntersection2(this.getVertex(interval[1]), eps);
    if(debug2)System.out.println(MapConstruction.startIndex+" I was called from here 2."+ in2);
    if(in2[0]>=0 && in2[0]<=1 && in2[1]>=0 && in2[1]<=1)
     vend = (in2[0]+in2[1])/2;
    else if(in2[0]>=0 && in2[0]<=1)vend=in2[0];
    else if(in2[1]>=0 && in2[1]<=1)vend=in2[1];
    else vend = 1;
   }
   if(debug)System.out.println("Final: "+interval[0]+" "+interval[1]);
   e.cstart = interval[0];
   e.cend = interval[1];
   e.vstart = vstart;
   e.vend = vend;
  
   return true;
  }
  catch(Exception ex)
  {
   System.out.println("eline: "+e.line.toString()+" "+e.line.m+" "+e.line.theta);
   System.out.println("this: "+ this.toString()+" "+this.m+" "+this.theta);
   System.out.println(i1+" "+i2+" "+i3+" "+i4);
   System.out.println(min1+" "+max1+" "+min2+" "+max2);
   System.out.println(this.getVertex(interval[0]).toString());
   System.out.println(this.getVertex(interval[1]).toString());
   System.out.println(detr+"  :  "+ Math.sqrt(Math.abs(detr)));
   System.out.println((-b_t + Math.sqrt(detr))/(2*a_t));
   System.out.println((-b_t - Math.sqrt(detr))/(2*a_t));
   /*System.out.println(interval[0]+": "+eps+"  " +this.getVertex(interval[0]).toString());
   System.out.println(interval[1]+": "+eps+"  " +this.getVertex(interval[1]).toString());
   System.out.println(in1[0]+" "+in1[1]);
   System.out.println(in2[0]+" "+in2[1]);*/
   System.out.println(ex.toString());
   System.exit(0);
   return false;
  }
 }
 
 public Vertex getVertex(double t)
 {
  return new Vertex(this.p1.x+this.xdiff*t, this.p1.y+this.ydiff*t);
 }
 public Line[] getEpsilonNeiborhood(Line vline, double eps)
 {
  
  Line line[] = new Line[2];
  double dx,dy;
  dx = eps*Math.cos(vline.theta + Math.PI/2);
  dy = eps*Math.sin(vline.theta + Math.PI/2);
  //dx_l =  eps*Math.cos(vline.theta + 3*Math.PI/2);
  //dy_l =  eps*Math.sin(vline.theta + 3*Math.PI/2);
   
  line[0] = new Line(new Vertex(vline.p1.x-dx, vline.p1.y-dy), new Vertex(vline.p2.x-dx, vline.p2.y-dy));
  line[1] = new Line(new Vertex(vline.p1.x+dx, vline.p1.y+dy), new Vertex(vline.p2.x+dx, vline.p2.y+dy));
 
  if( line[0].m != line[1].m ){
   
   //System.out.println("test slope "+line[0].m+" "+line[0].theta+" "+line[1].m+" "+line[1].theta);
   line[0].m = line[1].m;
   line[0].theta = line[1].theta;
  }
  return line;
 }
 public double distance(Vertex p)
 {
  
  double b_t = 2*((p1.x-p.x)*this.xdiff+(p1.y-p.y)*this.ydiff);
  double c_t = (p1.x-p.x)*(p1.x-p.x) + (p1.y-p.y)*(p1.y-p.y);// - eps*eps;
  double a_t = this.xdiff*this.xdiff + this.ydiff*this.ydiff;
  double disc = Math.sqrt((b_t*b_t - 4*a_t*c_t)/(4*a_t));
  double t[] = this.pIntersection(p, disc);
  if( t==null || t[0]>1 || t [0]<0 )return Math.min(Math.sqrt((p1.x-p.y)*(p1.x-p.y)+(p1.y-p.y)*(p1.y-p.y)), Math.sqrt((p2.x-p.y)*(p2.x-p.y)+(p2.y-p.y)*(p2.y-p.y)));
  else return disc;
 }
 public double[] getTParallel(Line line, double eps)
 {
  double t[]=new double[2];
  double newm; 
  double x1,y1,x2,y2;
  if(Math.abs(line.theta) == Math.PI/2)
  {
   newm = 0;
   x1 = this.p1.x;
   y1 = line.p1.y;
   x2 = this.p2.x;
   y2 = line.p2.y;
  }
  else if(Math.abs(line.theta) == 0)
  {
   newm = 0;
   x1 = line.p1.x;
   y1 = this.p1.y;
   x2 = line.p2.x;
   y2 = this.p2.y;
  }
  else{
   newm = 1/line.m;
   double c1 = line.p1.y + newm*line.p1.x;
   double c2 = line.p2.y + newm*line.p2.x;
  
   x1 = (c1-this.c)/(this.m-newm);
   y1 = this.m*x1+this.c;
  
   x2 = (c2-this.c)/(this.m-newm);
   y2 = this.m*x2+this.c;
  }
  
  if( Math.sqrt( (line.p1.x-x1)*(line.p1.x-x1) + (line.p1.y-y1)*(line.p1.y-y1)) > eps ) return null;
  if(this.xdiff!=0){
   t[0] = (x1-this.p1.x)/(this.p2.x - this.p1.x);
   t[1] = (x2-this.p1.x)/(this.p2.x - this.p1.x);
  }
  else
  {
   t[0] = (y1-this.p1.y)/(this.p2.y - this.p1.y);
   t[1] = (y2-this.p1.y)/(this.p2.y - this.p1.y);
  }
  
  return t;
 }
 /*public static void main(String args[])
 {
  //386850.0919848081 5817393.005136671; 387904.342 5817298.007
  Vertex v1 = new Vertex(390414.876637062, 5817947.478485119);
  Vertex v2 = new Vertex(389250.818, 5819078.555 );
  Vertex v3 = new Vertex(389504.28, 5818874.424);
  Vertex v4 = new Vertex(389504.33435079246, 5819055.313319193);
  Line l1 = new Line(v1,v2);
  double d[] = l1.pIntersection(v3, 160);
  System.out.println(d[0]+" "+d[1]);
  d = l1.pIntersection(v4, 160);
  System.out.println(d[0]+" "+d[1]);
 }
 public static void main(String args[])
 {
  Vertex v1 = new Vertex(396433.7289935143, 5825638.58657385);//new Vertex(10, 1);
  Vertex v2 = new Vertex(396438.3580216819, 5825621.230025792);//new Vertex(1.3,5);
  Vertex v3 = new Vertex(396109.288, 5823747.549);//new Vertex(1,3);
  Vertex v4 = new Vertex( 396111.314, 5823754.172);//new Vertex(2,9);
  Line l1 = new Line(v2,v1);
  Edge l2 = new Edge(v4,v3); 
  l1.pIntersection(l2, 1);
  //Vertex v = l1.getVertex(d[1]);
  //System.out.println(v.x+" "+v.y);
  //System.out.println(d[0]+" "+d[1]);
 }*/
}
