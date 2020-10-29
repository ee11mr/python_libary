#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:56:33 2020
Dictionary of sites used for generating FLEXPART back-trajectories

@author: mjr583
"""

site_dict = {
    'cvao' : {  'path' : '',
                'lllon' : -100., 
                'urlon' : 40., 
                'lllat' : -10., 
                'urlat' : 75,
                'polar' : False
                },
    'mace_head' : {  'path' : '',
                'lllon' : -100., 
                'urlon' : 40., 
                'lllat' : 15., 
                'urlat' : 85,
                'polar' : False
                },
    'tudor_hill' : {  'path' : '',
                'lllon' : -120., 
                'urlon' : 0., 
                'lllat' : 0., 
                'urlat' : 65,
                'polar' : False
                },
    'ragged_point' : {  'path' : '',
                'lllon' : -150., 
                'urlon' : -20., 
                'lllat' : -20., 
                'urlat' : 55,
                'polar' : False
                },
    'hateruma' : {  'path' : '',
                'lllon' : 75., 
                'urlon' : 180., 
                'lllat' : -20., 
                'urlat' : 50,
                'polar' : False
                },
    'neumayer' : {  'path' : '',
                'proj'  : 'spstere',
                'bounding_lat' : 30.,
                'lon_0' : 0., 
                'polar' : True
                },
    'south_pole' : {  'path' : '',
                'proj'  : 'spstere',
                'bounding_lat' : 30.,
                'lon_0' : 0., 
                'polar' : True
                }
    }
