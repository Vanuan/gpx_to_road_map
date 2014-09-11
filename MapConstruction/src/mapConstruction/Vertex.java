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
Filename: Vertex.java
 */

package mapConstruction;

import java.io.Serializable;

public class Vertex implements Serializable{

 /**
  * 
  */
 private static final long serialVersionUID = 1L;
 Long vertexID;
 double x, y, lat, lon;
 int degree=0;
 int adjacencyList[]=new int[15];
 double left=Double.MAX_VALUE, right=-1;//left and right endpoint of recheability interval or left is used as path label while computing shortest Paths.
 int startindex = -1;
 int endindex = 0;
 boolean done = false;
 double timestamp = -1;
// int paths[] = new int[10];
 
 public Vertex(Long vertexID, double lat, double lon, double x,double y)
 {
  this.vertexID = vertexID;
  this.lat = lat;
  this.lon = lon;
  this.x = x;
  this.y = y;
 }
 public Vertex(Long vertexID,double x,double y)
 {
  this.vertexID = vertexID;
  this.x = x;
  this.y = y;
 }
 public Vertex(double x,double y)
 {
  this.x = x;
  this.y = y;
 }
 public Vertex(double x,double y, double timestamp)
 {
  this.x = x;
  this.y = y;
  this.timestamp = timestamp;
 }
 void addElementAdjList(int v)
 {
  adjacencyList[degree] = v;
  degree++;
 }
 public String toString()
 {
  //return this.vertexID+" "+this.x+" "+this.y+" "+this.lat+" "+this.lon+" ";
  return this.degree+" "+this.x+" "+this.y;
 }
 
 public int getIndexAdjacent(int k)
 {
  for(int i=0;i<this.degree;i++)
  {
   if(this.adjacencyList[i] == k) return i;
   
  }
  return -1;
 }
 /*public boolean checkDone()
 {
  for(int i=0;i<degree;i++)if( paths[i] == 0 )return false;
  return true;
 }
 public int nextVertex()
 {
  for(int i=0;i<degree;i++)if( paths[i] == 0 ){ return i;}
  return -1;
 }*/
 public double dist(Vertex v2)
 {
  return Math.sqrt(Math.pow(this.x-v2.x, 2)+Math.pow(this.y-v2.y, 2));
 }
 public void removeDuplicates()
 {
  for(int i=0;i<this.degree;i++)
  {
   for(int j = i+1;j < this.degree;j++)
   {
    if(this.adjacencyList[i] == this.adjacencyList[j])
    {
     for(int k=j;k<this.degree-1;k++)
     {
      this.adjacencyList[k] = this.adjacencyList[k+1];
     }
     this.degree--;
     //System.out.println("duplicate removed"+this.degree);
    }
    
   }
  }  
  
 }
 
 public void reset()
 {
  left=Double.MAX_VALUE;
  right=-1;
  startindex = -1;
  endindex = 0;
  //paths = new int[10];
  done = false;
 }
 
}
