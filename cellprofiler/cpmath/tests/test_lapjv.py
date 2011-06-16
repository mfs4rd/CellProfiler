'''test_lapjv.py - test the Jonker-Volgenant implementation

This software is provided under the BSD License

Copyright (c) 2011 Broad Institute All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer. Redistributions in binary form 
must reproduce the above copyright notice, this list of conditions and the 
following disclaimer in the documentation and/or other materials provided with 
the distribution. Neither the name of the Broad Institute nor the names of its 
contributors may be used to endorse or promote products derived from this 
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import numpy as np
import scipy.ndimage as scind
import unittest

import cellprofiler.cpmath.lapjv as LAPJV
from cellprofiler.cpmath.filter import permutations

class TestLAPJVPYX(unittest.TestCase):
    def test_01_01_reduction_transfer(self):
        '''Test the reduction transfer implementation'''
        
        cases = [
            dict(i = [ 0, 1, 2 ],
                 j = [ 0, 1, 2, 0, 1, 2, 0, 1, 2],
                 idx = [ 0, 3, 6 ],
                 count = [ 3, 3, 3 ],
                 x = [ 2, 0, 1],
                 y = [ 1, 2, 0],
                 c = [ 5.0, 4.0, 1.0, 2.0, 6.0, 4.0, 4.0, 3.0, 7.0],
                 u_in = [ 0.0, 0.0, 0.0 ],
                 v_in = [ 1.0, 2.0, 3.0 ],
                 u_out = [ 2.0, 3.0, 6.0 ],
                 v_out = [ -2.0, -4.0, 1.0 ]),
            dict(i = [ 1, 2, 3 ],
                 j = [ 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
                 idx = [ 0, 3, 6, 9 ],
                 count = [ 3, 3, 3, 3 ],
                 x = [ 3, 2, 0, 1],
                 y = [ 1, 2, 0, 3],
                 c = [ 0.0, 0.0, 0.0, 5.0, 4.0, 1.0, 2.0, 6.0, 4.0, 4.0, 3.0, 7.0],
                 u_in = [ 0.0, 0.0, 0.0, 0.0 ],
                 v_in = [ 1.0, 2.0, 3.0, 0.0 ],
                 u_out = [ 0.0, 2.0, 3.0, 6.0 ],
                 v_out = [ -2.0, -4.0, 1.0, 0.0 ]),
        ]
        for case in cases:
            u = np.ascontiguousarray(case["u_in"], np.float64)
            v = np.ascontiguousarray(case["v_in"], np.float64)
            LAPJV.reduction_transfer(
                np.ascontiguousarray(case["i"], np.uint32),
                np.ascontiguousarray(case["j"], np.uint32),
                np.ascontiguousarray(case["idx"], np.uint32),
                np.ascontiguousarray(case["count"], np.uint32),
                np.ascontiguousarray(case["x"], np.uint32),
                u,v,
                np.ascontiguousarray(case["c"], np.float64))
            expected_u = np.array(case["u_out"])
            expected_v = np.array(case["v_out"])
            np.testing.assert_array_almost_equal(expected_u, u)
            np.testing.assert_array_almost_equal(expected_v, v)
            
    def test_02_01_augmenting_row_reduction(self):
        
        cases = [
            dict(n=3,
                 ii = [ 1 ],
                 jj = [ 0, 1, 2, 0, 1, 2, 0, 1, 2],
                 idx = [ 0, 3, 6],
                 count = [ 3, 3, 3],
                 x = [ 1, 3, 0],
                 y = [ 2, 0, 3],
                 u_in = [ 1.0, 2.0, 3.0 ],
                 v_in = [ 1.0, 2.0, 3.0 ],
                 c = [ 3.0, 6.0, 5.0, 5.0, 5.0, 7.1, 8.0, 11.0, 9.0],
                 u_out = [1.0, 2.0, 3.0],
                 v_out = [1.0, 1.0, 3.0],
                 x_out = [ 2, 1, 0],
                 y_out = [ 2, 1, 0])]
        for case in cases:
            u = np.ascontiguousarray(case["u_in"], np.float64)
            v = np.ascontiguousarray(case["v_in"], np.float64)
            x = np.ascontiguousarray(case["x"], np.uint32)
            y = np.ascontiguousarray(case["y"], np.uint32)
            LAPJV.augmenting_row_reduction(
                case["n"],
                np.ascontiguousarray(case["ii"], np.uint32),
                np.ascontiguousarray(case["jj"], np.uint32),
                np.ascontiguousarray(case["idx"], np.uint32),
                np.ascontiguousarray(case["count"], np.uint32),
                x, y, u, v,
                np.ascontiguousarray(case["c"], np.float64))
            expected_u = np.array(case["u_out"])
            expected_v = np.array(case["v_out"])
            expected_x = np.array(case["x_out"])
            expected_y = np.array(case["y_out"])
            np.testing.assert_array_almost_equal(expected_u, u)
            np.testing.assert_array_almost_equal(expected_v, v)
            np.testing.assert_array_equal(expected_x, x)
            np.testing.assert_array_equal(expected_y, y)

    def test_03_01_augment(self):
        cases = [
            dict(n = 3,
                 i = [ 2],
                 j = [ 0, 1, 2, 0, 1, 2, 0, 1, 2],
                 idx = [0, 3, 6],
                 count = [3,3,3],
                 x_in = [ 0, 1, 3],
                 x_out = [ 0, 1, 2],
                 y_in = [ 0, 1, 3],
                 y_out = [ 0, 1, 2],
                 u_in = [ 4, 0, 2],
                 v_in = [-1, 1, 1],
                 u_out = [4, 0, 2],
                 v_out = [-1, 1, 1],
                 c = [3, 5, 7, 4, 1, 6, 2, 3, 3])]
        for case in cases:
            n = case["n"]
            i = np.ascontiguousarray(case["i"], np.uint32)
            j = np.ascontiguousarray(case["j"], np.uint32)
            idx = np.ascontiguousarray(case["idx"], np.uint32)
            count = np.ascontiguousarray(case["count"], np.uint32)
            x = np.ascontiguousarray(case["x_in"], np.uint32)
            y = np.ascontiguousarray(case["y_in"], np.uint32)
            u = np.ascontiguousarray(case["u_in"], np.float64)
            v = np.ascontiguousarray(case["v_in"], np.float64)
            c = np.ascontiguousarray(case["c"], np.float64)
            LAPJV.augment(n, i, j, idx, count, x, y, u, v, c)
            np.testing.assert_array_equal(x, case["x_out"])
            np.testing.assert_array_equal(y, case["y_out"])
            np.testing.assert_almost_equal(u, case["u_out"])
            np.testing.assert_almost_equal(v, case["v_out"])
        
            
class TestLAPJV(unittest.TestCase):
    def test_01_02(self):
        r = np.random.RandomState()
        r.seed(11)
        for reductions in [0,2]:
            for _ in range(100):
                c = r.randint(1,10,(5,5))
                i,j = np.mgrid[0:5,0:5]
                i = i.flatten()
                j = j.flatten()
                x,y,u,v = LAPJV.lapjv(i, j, c.flatten(), True, reductions)
                min_cost = np.sum(c)
                best = None
                for permutation in permutations([0,1,2,3,4]):
                    cost = sum([c[i,permutation[i]] for i in range(5)])
                    if cost < min_cost:
                        best = list(permutation)
                        min_cost = cost
                result_cost = sum([c[i,x[i]] for i in range(5)])
                self.assertAlmostEqual(min_cost, result_cost)
                
    def test_01_03(self):
        '''Regression test of a matrix that crashed lapjv'''
        d = np.array([[  0.        ,   0.        ,   0.        ],
                      [  1.        ,   1.        ,   5.34621029],
                      [  1.        ,   7.        ,  55.        ],
                      [  2.        ,   2.        ,   2.09806089],
                      [  2.        ,   8.        ,  55.        ],
                      [  3.        ,   3.        ,   4.82063029],
                      [  3.        ,   9.        ,  55.        ],
                      [  4.        ,   4.        ,   3.99481917],
                      [  4.        ,  10.        ,  55.        ],
                      [  5.        ,   5.        ,   3.18959054],
                      [  5.        ,  11.        ,  55.        ],
                      [  6.        ,   1.        ,  55.        ],
                      [  6.        ,   7.        ,   0.        ],
                      [  6.        ,   8.        ,   0.        ],
                      [  6.        ,   9.        ,   0.        ],
                      [  6.        ,  10.        ,   0.        ],
                      [  6.        ,  11.        ,   0.        ],
                      [  7.        ,   2.        ,  55.        ],
                      [  7.        ,   7.        ,   0.        ],
                      [  7.        ,   8.        ,   0.        ],
                      [  7.        ,   9.        ,   0.        ],
                      [  7.        ,  10.        ,   0.        ],
                      [  7.        ,  11.        ,   0.        ],
                      [  8.        ,   3.        ,  55.        ],
                      [  8.        ,   7.        ,   0.        ],
                      [  8.        ,   8.        ,   0.        ],
                      [  8.        ,   9.        ,   0.        ],
                      [  8.        ,  10.        ,   0.        ],
                      [  8.        ,  11.        ,   0.        ],
                      [  9.        ,   4.        ,  55.        ],
                      [  9.        ,   7.        ,   0.        ],
                      [  9.        ,   8.        ,   0.        ],
                      [  9.        ,   9.        ,   0.        ],
                      [  9.        ,  10.        ,   0.        ],
                      [  9.        ,  11.        ,   0.        ],
                      [ 10.        ,   5.        ,  55.        ],
                      [ 10.        ,   7.        ,   0.        ],
                      [ 10.        ,   8.        ,   0.        ],
                      [ 10.        ,   9.        ,   0.        ],
                      [ 10.        ,  10.        ,   0.        ],
                      [ 10.        ,  11.        ,   0.        ],
                      [ 11.        ,   6.        ,  55.        ],
                      [ 11.        ,   7.        ,   0.        ],
                      [ 11.        ,   8.        ,   0.        ],
                      [ 11.        ,   9.        ,   0.        ],
                      [ 11.        ,  10.        ,   0.        ],
                      [ 11.        ,  11.        ,   0.        ]])
        x,y = LAPJV.lapjv(d[:,0].astype(int), d[:,1].astype(int), d[:,2])
        c = np.ones((12,12)) * 1000000
        c[d[:,0].astype(int), d[:,1].astype(int)] = d[:,2]
        self.assertTrue(np.sum(c[np.arange(12),x]) < 74.5)
        self.assertTrue(np.sum(c[y,np.arange(12)]) < 74.5)
        