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
Filename: IntervalComparatorEdge.java
 */
package mapConstruction;

import java.util.Comparator;


public class IntervalComparatorEdge implements Comparator<Edge>{
 @Override
    public int compare(Edge x, Edge y)
    {
        // Assume neither string is null. Real code should
        // probably be more robust
       
        if(x.cstart < y.cstart)
        {
         return -1;
        }
        else if(x.cstart > y.cstart)
        {
         return 1;
        }
        else
        {
         if (x.cend < y.cend)
         {
          return -1;
         }
         if (x.cend > y.cend)
         {
          return 1;
         } 
         return 0;
        }
       
    }
 
}