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
Filename: Edge.java
 */
package mapConstruction;

public class Edge {
 
 Vertex v1,v2;
 int eid;
 double cstart,cend;
 double vstart,vend;
 Line line;
 boolean done;
 int startIndex, endIndex;
 Edge(Vertex v1,Vertex v2,int eid)
 {
  this.v1 = v1;
  this.v2  = v2;
  this.cstart = Double.MAX_VALUE;
  this.cend = -1;
  this.vstart = Double.MAX_VALUE;
  this.vend = -1;
  this.line = new Line(v1,v2);
  this.done = false;
  this.eid = eid;
 }
 void reset()
 {
  this.cstart = Double.MAX_VALUE;
  this.cend = -1;
  this.vstart = Double.MAX_VALUE;
  this.vend = -1;
  this.line = new Line(v1,v2);
  this.done = false;
 }
 
 public String toString()
 {
  return new String(v1.toString() + v2.toString());
 }
}
