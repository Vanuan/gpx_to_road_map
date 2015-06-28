
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
Filename: MapConstruction.java
 */
package mapConstruction;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.PriorityQueue;
import java.util.StringTokenizer;

public class MapConstruction 
{

 /**
  * @param args
  */
 public static int curveid;
 public String curveName;
 public static int startIndex = 0;
 public int eid=0;
 public ArrayList<Vertex> readFileBenchmark(String fileName)
 {
  
  ArrayList<Vertex> curves = new ArrayList<Vertex>();
   try 
   {
    BufferedReader in = new BufferedReader(new FileReader(fileName));
       String str;            
       while ((str = in.readLine()) != null) {
           if(str.equals(""))continue;
        StringTokenizer strToken = new StringTokenizer(str,",");
        strToken.nextToken();
        Double d = new Double(strToken.nextToken());
           double p1 = d.doubleValue();
           d = new Double(strToken.nextToken());
           double p2 = d.doubleValue();
          
           //strToken.nextToken();
           //strToken.nextToken();
          
           /*double hour = Double.parseDouble(strToken.nextToken());
           double minute = Double.parseDouble(strToken.nextToken());
           double second = Double.parseDouble(strToken.nextToken());
           */
           double time = Double.parseDouble(strToken.nextToken());
           
           curves.add(new Vertex(p1,p2,time));
          
          }
       in.close();
      
   } 
   catch (IOException e) {
    System.out.println(fileName+" "+e.toString());
    //System.exit(0);
   }
   
   //System.out.println("End Reading File...");
   return curves;
  }

 public ArrayList<Vertex> readFile(String fileName)
 {
  
  ArrayList<Vertex> curves = new ArrayList<Vertex>();
   try 
   {
    BufferedReader in = new BufferedReader(new FileReader(fileName));
       String str;            
       while ((str = in.readLine()) != null) {
           if(str.equals(""))continue;
        StringTokenizer strToken = new StringTokenizer(str);
           Double d = new Double(strToken.nextToken());
           double p1 = d.doubleValue();
           d = new Double(strToken.nextToken());
           double p2 = d.doubleValue();
          
          /* strToken.nextToken();
           strToken.nextToken();
          
           double hour = Double.parseDouble(strToken.nextToken());
           double minute = Double.parseDouble(strToken.nextToken());
           double second = Double.parseDouble(strToken.nextToken());
           double time = (hour*60+minute)*60+second;*/
           double time = Double.parseDouble(strToken.nextToken());
           
           curves.add(new Vertex(p1,p2,time));
          
          }
       in.close();
      
   } 
   catch (IOException e) {
    System.out.println(fileName+" "+e.toString());
    //System.exit(0);
   }
   
   //System.out.println("End Reading File...");
   return curves;
  }

 
 public boolean computeInterval(Edge e, ArrayList<Vertex> curves, int cur, double eps)
 {
  Line line = new Line(curves.get(cur-1),curves.get(cur));  
  return line.pIntersection(e, eps);
 }
 
 public Edge computeNextInterval(Edge e, ArrayList<Vertex> curves,int newstart,double eps)
 {
  /****************************startintex-----interval--------endindex*************************************/
  //System.out.println("I am inside next interval.");
  boolean debug = false;
  //if(e==null){ System.out.println("Edge is null."); }
  
  boolean first = true;
  
  int startIndex=0;
  double cstart=0, vstart=0;
  
  if( newstart >= curves.size())
  {
   e.endIndex = curves.size();
   e.done = true;
   return e;
  }
  
  
  for(int i = newstart; i < curves.size(); i++ )
  {
   MapConstruction.startIndex = i;
   boolean result = computeInterval(e,curves,i,eps);
   
   if(debug)System.out.println("i (next interval) = "+i +"  "+first+" "+result);
   if(first && result)
   {
    startIndex = i-1;
    cstart = e.cstart;
    vstart = e.vstart;
    
    first = false;
    
    if(e.cend<1)
    {
     e.startIndex = startIndex;
     e.cstart = startIndex+cstart;
     e.vstart = vstart;
     e.cend = i-1+e.cend;
     e.endIndex = i;
     return e;
    }
   }
   else if(!first && result)
   {
    if(e.cend<1)
    {
     e.startIndex = startIndex;
     e.cstart = startIndex+cstart;
     e.vstart = vstart;
     e.cend = i-1+e.cend;
     e.endIndex = i;
     return e;
    }
   }
   else if(!first && !result)
   {
    e.startIndex = startIndex;
    e.cstart = startIndex+cstart;
    e.vstart = vstart;
    e.cend = i-1+e.cend;
    e.endIndex = i;
    return e;
   }
   
  }
  
  if(first)
  {
   e.endIndex = curves.size();
   e.done = true;
  }
  else
  {
   e.startIndex = startIndex;
   e.cstart = startIndex+cstart;
   e.vstart = vstart;
   
   e.cend = curves.size()-2+e.cend;
   e.endIndex = curves.size()-2;
  }
 
 
  return e;
 }
 
 public void updateMap (ArrayList<Vertex> vList, HashMap<String, Integer> map, Edge e)
 {
  
  Vertex v;
  int parent = -1;
  int child = -1;
  boolean debug = false;
  String keyParent = e.v1.x+" "+e.v1.y;
  String keyChild = e.v2.x+" "+e.v2.y;
  
  if(map.containsKey(keyParent))
  {
   parent = map.get(keyParent).intValue();
  }
  else
  {
   v = e.v1;
   vList.add(v);
   parent = vList.indexOf(v);
   map.put(keyParent, parent);
  }
  
  if(map.containsKey(keyChild))
  {
   child = map.get(keyChild).intValue();
  }
  else
  {
   v = e.v2;
   vList.add(v);
   child = vList.indexOf(v);   
   map.put(keyChild, child);
  }
  
  
  
  if(parent!=-1 && child!=-1 && parent!=child)
  {
   vList.get(parent).addElementAdjList(child);
   vList.get(child).addElementAdjList(parent);
   if(debug){System.out.println("map updated...");System.out.println("child, parent :"+child+", "+parent);}
   if(vList.get(parent).dist(vList.get(child))>10000)System.exit(0);
  
  }
  
  
 }
 
 public void edgeSplit(ArrayList<Vertex> vList, HashMap<String, Integer> map, Vertex v1, Vertex v2, Vertex v)
 {
  String key1 = v1.x+" "+v1.y;
  String key2 = v2.x+" "+v2.y;
  String key = v.x+" "+v.y;
  
  int index1 = map.get(key1).intValue();
  int index2 = map.get(key2).intValue();
  int index = map.get(key).intValue();
  
  for(int i=0;i<v1.degree;i++)
  {
   if(v1.adjacencyList[i] == index2)
   {
    v1.adjacencyList[i] = index;
   }
  }
  
  for(int i=0;i<v2.degree;i++)
  {
   if(v2.adjacencyList[i] == index1)
   {
    v2.adjacencyList[i] = index;
   }
  }
   
 }
 public void mapConstruction(ArrayList<Vertex> vList, ArrayList<Edge> graph, HashMap<String, Integer> map, ArrayList<Vertex> curves, double eps, boolean connect)
 {
  boolean debug = false, checkt = false;
  //if(MapConstruction.curveid==52) debug=true;
  //boolean connect = true;
  Comparator<Edge> comparator = new IntervalComparatorEdge();
  PriorityQueue<Edge> pq = new PriorityQueue<Edge>(21282,comparator);
  double factor = 10*eps;
  for(int i=0; i < graph.size(); i++)
  { 
   this.computeNextInterval(graph.get(i), curves, 1, eps);
   if(!graph.get(i).done)
   { 
    /*if(debug){
     System.out.println(i+" "+curves.size()+"  "+graph.get(i).cstart+" "+graph.get(i).cend +" "+graph.get(i).vstart +" "+graph.get(i).vend);
     System.out.println(graph.get(i).toString());
    }*/
    pq.add(graph.get(i));
   }
  }
  
  
  //The whole curve will be added as an edge
  
  if(pq.isEmpty()) 
  {
   
   if(debug)System.out.println(this.curveName+" inserted as an edge");
   for(int i=0; i < curves.size()-1; i++)
   {
    
    this.updateMap(vList, map, new Edge(curves.get(i),curves.get(i+1),this.eid++));
   }
   if(debug)System.out.println(this.curveName+" inserted as an edge");
   return;
  }
  
  Edge e = pq.poll();
  //System.out.println(curves.size()+"  "+e.cstart+" "+e.cend);
  double cend = e.cend;
  Edge cedge = e;
  
  if(e.cstart > 0) 
  {
   if(debug)System.out.println(this.curveName+" inserted as an edge until "+e.cstart);
   
   for(int i = 0;i < Math.floor(e.cstart); i++)
   {
    this.updateMap(vList, map, new Edge(curves.get(i),curves.get(i+1),this.eid++));
   }
   
   int  index = (int)Math.floor(e.cstart);
   Line newLine = new Line(curves.get(index),curves.get(index+1));
   double t = e.cstart - Math.floor(e.cstart);
   
   if(!checkt || (t > 0 && t < 1)){    
    this.updateMap(vList, map, new Edge (curves.get(index),newLine.getVertex(t),this.eid++));
    
   }
   else
   {
    System.out.println("case 1 t="+t);
   }
   
   if(connect && newLine.getVertex(t).dist(e.line.getVertex(e.vstart)) <= factor)
   {
    this.updateMap(vList, map, new Edge (newLine.getVertex(t), e.line.getVertex(e.vstart),this.eid++));
    this.edgeSplit(vList, map, e.v1, e.v2, e.line.getVertex(e.vstart));
   } 
  
   
  //need to add rest of the line segment
   //return false;
  }
  
  while( cend < curves.size() )
  {
   
   if(cend < e.cend)
   {
    if(debug)System.out.println(this.curveName+" has white interval " + e.cstart+" "+e.cend+" " + cend+" "+e.vstart+" "+e.vend);
    
    cend = e.cend;
    cedge = e;
   }
   
   if( e.cend == curves.size()-1 ) {
    if(debug)System.out.println(this.curveName+" processing completed.");
    return;
   }
   
   
   this.computeNextInterval(e, curves, e.endIndex+1, eps);
   MapConstruction.startIndex = e.endIndex+1;
   if(!e.done) pq.add(e);
   
   if(pq.isEmpty()) 
   {
    if(debug)System.out.println(this.curveName+" inserted as an edge from " + cend + " to end");
    //need to add rest of the line segment
    
    //cend = e.cend;
    //cedge = e;
    
    int  index = (int)Math.floor(cend);    
    Line newLine = new Line(curves.get(index),curves.get(index+1));
    double t = cend - Math.floor(cend);
    
    
    if(connect && cedge.line.getVertex(cedge.vend).dist(newLine.getVertex(t)) <= factor)
    {
     this.updateMap(vList, map, new Edge (cedge.line.getVertex(cedge.vend),newLine.getVertex(t),this.eid++));
     this.edgeSplit(vList, map, cedge.v1, cedge.v2, cedge.line.getVertex(cedge.vend));
     
    }
    
    // need to break edge
    
    
    if(!checkt || (t > 0 && t < 1)){
     this.updateMap(vList, map, new Edge (newLine.getVertex(t),curves.get(index+1),this.eid++));
    }
    else
    {
     System.out.println("case 2 t="+t);
    }
    
    for(int i= index + 1 ;i < curves.size()-1; i++)
    {
     this.updateMap(vList, map, new Edge(curves.get(i),curves.get(i+1),this.eid++));
    }
    return;
   }
   
   e = pq.poll();
   
   if( e.cstart > cend )
   {
    
    if(debug)System.out.println(this.curveName+" inserted as an edge from " + cend + " to "+e.cstart+" "+e.eid);
    
    //need to add rest of the line segment
    
    int  index = (int)Math.floor(cend);
    Line newLine = new Line(curves.get(index),curves.get(index+1));
    double t = cend-Math.floor(cend);
    
    int  index_start = (int)Math.floor(e.cstart);
    if(connect && cedge.line.getVertex(cedge.vend).dist(newLine.getVertex(t)) <= factor)
    {
     this.updateMap(vList, map, new Edge (cedge.line.getVertex(cedge.vend),newLine.getVertex(t),this.eid++));
     this.edgeSplit(vList, map, cedge.v1, cedge.v2, cedge.line.getVertex(cedge.vend));
         
    }
    if(debug)System.out.println("first case.");
    
    if(index==index_start)
    {
     this.updateMap(vList, map, new Edge (newLine.getVertex(t),newLine.getVertex(e.cstart-index_start),this.eid++));
     index = (int)Math.floor(e.cstart);
     newLine = new Line(curves.get(index),curves.get(index+1));
     t = e.cstart - Math.floor(e.cstart);
    }
    else{
    if(!checkt || (t > 0 && t < 1)){    
     
     this.updateMap(vList, map, new Edge (newLine.getVertex(t),curves.get(index+1),this.eid++));
    }
    else
    {
     System.out.println("case 3 t="+t);
    }
    if(debug)System.out.println("second case.");
    
    for(int i = index+1; i < Math.floor(e.cstart); i++)
    {
     this.updateMap(vList, map, new Edge(curves.get(i),curves.get(i+1),this.eid++));
    }
    
    if(debug)System.out.println("third loop case.");
    index = (int)Math.floor(e.cstart);
    newLine = new Line(curves.get(index),curves.get(index+1));
    t = e.cstart - Math.floor(e.cstart);
    
    if(!checkt || (t > 0 && t < 1)){
     
     this.updateMap(vList, map, new Edge (curves.get(index),newLine.getVertex(t),this.eid++));
    }
    else
    {
     System.out.println("case 4 t="+t);
    }
    if(debug)System.out.println("fourth case.");
    }
    
    if( connect && newLine.getVertex(t).dist( e.line.getVertex(e.vstart)) <= factor )
    {
     this.updateMap(vList, map, new Edge (newLine.getVertex(t), e.line.getVertex(e.vstart),this.eid++));
     this.edgeSplit(vList, map, e.v1, e.v2, e.line.getVertex(e.vstart));
     
    }
    
    if(debug)System.out.println("fifth case.");
    
    //return false;
   }
   
   
  }
  
  
  return;
  /*int cur = 0;
  
  Comparator<Edge> comparator = new IntervalComparator();
  PriorityQueue<Edge> pq = new PriorityQueue<Edge>(1000,comparator);
  
  for(int i=0;i<vList.size();i++)
  {
   Vertex v1 = vList.get(i);
   for(int j=0;j<v1.degree;j++)
   {
    Vertex v2 = vList.get(v1.adjacencyList[j]);
    if(!(v1.x ==v2.x && v1.y == v2.y))
    {
     Edge e = new Edge(v1,v2);
     this.computeNextInterval(e, curves, cur, eps);
     if(!e.done)pq.add(e);
    }
   }
  }
  
  Edge prev =pq.poll();
  
  if(prev == null)
  {
   
   int i = 1;
   while(i<curves.size())
   {
    this.updateMap(vList, map, new Edge(curves.get(i-1),curves.get(i)));
    i++;
   }
   return;
  }
  else
  {
   System.out.println("I am not a new curve.");
  }
  
  
  while(cur<curves.size() && !pq.isEmpty())
  {
   if(prev.cstart > cur )
   {
    int i = cur;
    while(i<prev.startIndex)
    {
     updateMap(vList,  map, new Edge(curves.get(i-1),curves.get(i)));
    }
    Line line = new Line(curves.get(i-1),curves.get(i));
    updateMap(vList,  map, new Edge(curves.get(i-1),line.getVertex(prev.cstart)));
    updateMap(vList,  map, new Edge(line.getVertex(prev.cstart),prev.line.getVertex(prev.vstart)));
   }
  
  
   cur = prev.endIndex;
   
   
   
   System.out.println(pq.isEmpty()+" "+pq.peek().toString()+ prev.toString());
   System.out.println("prev "+prev.cstart +"  " + prev.cend);
   
   Edge e = pq.poll();
   
   System.out.println("e "+e.cstart +"  " + e.cend);
   System.out.println(e.cstart < prev.cend);
   
   while( e != null && e.cstart < prev.cend )
   {
    if(prev.cend < e.cend)
    {
     prev = e;
     cur = e.endIndex;
    }
    this.computeNextInterval(e, curves, e.endIndex, eps);
    if(!e.done)pq.add(e);    
    e = pq.poll();
     
   }
   
   Line line = new Line(curves.get(cur-1),curves.get(cur));
   updateMap(vList,  map, new Edge(line.getVertex(prev.cend),prev.line.getVertex(prev.vend)));
   updateMap(vList,  map, new Edge(curves.get(cur -1),line.getVertex(prev.cend)));
  }*/
 }
 
 public void writeToFile(ArrayList<Vertex> vList, String fileName)
 {
  try{
  BufferedWriter bwways = new BufferedWriter ( new FileWriter (fileName));
  boolean write = false;
  for(int i=0;i<vList.size();i++)
  {
   Vertex v = vList.get(i);
   for(int j=0; j< v.degree;j++)
   {
    Vertex v1 = vList.get(v.adjacencyList[j]);
    write = true;
    bwways.write(v.x+" "+v1.x+" "+v.y+" "+v1.y+"\n");
   }
  }
  System.out.println("Write completed "+write);
  bwways.close();
  }
  catch(Exception ex)
  {
   System.out.println(ex.toString());
  }
  
  try{
   int count = 0;
   BufferedWriter bwedges = new BufferedWriter ( new FileWriter (fileName+"edges.txt"));
   BufferedWriter bvertex = new BufferedWriter ( new FileWriter (fileName+"vertices.txt"));
   
   boolean write = false;
   for(int i=0;i<vList.size();i++)
   {
    Vertex v = vList.get(i);
    bvertex.write(i+","+v.x+","+v.y+"\n");
    
    for(int j=0; j< v.degree;j++)
    {
     write = true;
     bwedges.write(count+","+i+","+v.adjacencyList[j]+"\n");
     count++;
    }
   }
   System.out.println("Write completed "+write);
   bwedges.close();
   bvertex.close();
   }
   catch(Exception ex)
   {
    System.out.println(ex.toString());
   }
 }
 
 public void mapConstructionCurves(ArrayList<Vertex> vList, HashMap<String,Integer> map, ArrayList<Vertex> curves, double eps, boolean connect)
 {
  ArrayList<Edge> graph = new ArrayList<Edge>();
  this.eid = 0;
  for(int i=0;i<vList.size();i++)
  {
   Vertex v = vList.get(i);
   for(int j=0;j<v.degree;j++)
   {
    Vertex v1 = vList.get(v.adjacencyList[j]);
    if(!v.equals(v1))graph.add(new Edge(v,v1,this.eid++));
   }
  }
  
  this.mapConstruction(vList, graph, map, curves, eps, connect);
 }
 
 public ArrayList<Vertex> removeDuplicates(ArrayList<Vertex> curves)
 {
  for(int i = 1;i<curves.size();i++)
  {
   Vertex prev = curves.get(i-1);
   Vertex cur = curves.get(i);
   
   if(prev.x == cur.x && prev.y == cur.y)
   {
    curves.remove(i);
    i--;
   }
   
  }
  return curves;
 }
 public static void main(String[] args) {
  // TODO Auto-generated method stub
  //String cityName = "chicago";
  String cityName = "berlin_large";
  
  //String filePath = "E://Map Construction2//curves//DesiredInputFiles";
  //String filePath = "E://Map Construction2//curves//berlin_20070612";
  //String filePath = "E://Map Construction2//curves/ATH_GPS";
  String filePath = "E://map_generation_benchmark//data//"+cityName+"//tracking_data//data";
  //String filePath = "E://map_generation_benchmark//data//"+cityName+"//tracking_data//trips_utm16N";
  int time_const = 120;
  boolean connect = true;
  File folder = new File(filePath);
  ArrayList<Vertex> curves;
  MapConstruction mc = new MapConstruction();
  int k=0;
  //int eps = 80;
  int maxsize = 200;
  
  for ( int eps = 150; eps<=200; eps+=10){
   System.out.println("processing eps = "+eps);
   HashMap<String, Integer> map = new HashMap<String,Integer>();
   ArrayList<Vertex> rMap = new ArrayList<Vertex>();
  for(File file: folder.listFiles())
  {
   //System.out.println("processing file "+k+" "+file.getName());
   //if(k>52)break;
   if(file.isDirectory())continue;
   
   mc.curveid = k;
   mc.curveName = file.getName();
   if(cityName.endsWith("large"))curves = mc.readFile(file.getAbsolutePath());
   else{
    curves = mc.readFileBenchmark(file.getAbsolutePath());
   }
    curves = mc.removeDuplicates(curves);
   if(curves.size() < 2) continue;
   //if(curves.size()> maxsize)
   //{
    
    int i=0;
    
    while( i < curves.size())
    {
     //System.out.println("processing file "+k+"( "+i+" )"+file.getName());
     ArrayList<Vertex> newCurves = new ArrayList<Vertex>();
     boolean skip = false;
     newCurves.add(curves.get(i));
     i++;
     if(i==curves.size())break;
     newCurves.add(curves.get(i));
     
     if(i<curves.size()  && (curves.get(i).timestamp - curves.get(i-1).timestamp > time_const)) continue;
     i++;
     //System.out.println(i);
     while( i < curves.size())//i%maxsize!=0 &&
     {
      
      
      //System.out.println(curves.get(i).timestamp - curves.get(i-1).timestamp);
      if(i<curves.size() && (curves.get(i).timestamp - curves.get(i-1).timestamp > time_const ))
      {
       //System.out.println(curves.get(i).timestamp - curves.get(i-1).timestamp);
       
       //System.out.println("skip true.");
       skip = true;
       break; 
      }
      newCurves.add(curves.get(i));
      i++;
     }
     if(!skip)i--;
     if(newCurves.size()>1)mc.mapConstructionCurves(rMap, map, newCurves, eps, connect);
     
    }
   /*}
   else
   {
    mc.mapConstructionCurves(rMap, map, curves,eps, connect);
   }*/
   k++;
   
   //if(k > 368 )break;
   
  }
  //mc.writeToFile(rMap, "E://map_generation_benchmark//data//athens//algorithms//mahmuda//graphAth"+eps);
  String outputPath = "E://map_generation_benchmark//data//"+cityName+"//algorithms//mahmuda_"+time_const+"//";
  
  File file = new File(outputPath+eps+"//");
  if(!file.exists())
  {
   if (file.mkdirs()) 
   {
    System.out.println("Directory is created!");
   } 
   else 
   {
    System.out.println("Failed to create directory!");
   }
  }
  
  mc.writeToFile(rMap, outputPath+eps+"//"+cityName+"_mahmuda_");
  
  //need to write the graph
 }
 }

}
