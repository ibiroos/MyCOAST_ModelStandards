#!/bin/env python
# -*- coding: utf-8 -*-

import string
from glob import glob
from datetime import datetime, timedelta

import argparse

import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

configurations = {}

PATH = '/mnt/netapp_ext2/Store_Meteo/'

configurations['WW3'] = {
    'mallas'  : 
            {'atn'     : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_atn_${ano}${mes}${dia}_${ciclo}00.nc'}    , 
             'iberia'  : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_iberico_${ano}${mes}${dia}_${ciclo}00.nc'}, 
             'galicia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_galicia_${ano}${mes}${dia}_${ciclo}00.nc'},
            },
    'version' : 1     ,
    'tipo'    : 'ANPR',
    'offset'  : 0,
}

configurations['ROMS'] = {
    'mallas'   : {'iberia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/ROMS_GEOPOT/${ano}${mes}${dia}/${ciclo}/roms_002_${ano}${mes}${dia}_${ciclo}00.nc'},
                 },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

configurations['WRF'] = {
    'mallas'   : 
               {'galicia' : {'file_template' : '%s/OP/DATOS/PRODUCTOS/METEOSIX/${ano}${mes}${dia}/${ciclo}/wrf_arw_det_history_d03_${ano}${mes}${dia}_${ciclo}00.nc4' % PATH},
                'iberia'  : {'file_template' : '%s/OP/DATOS/PRODUCTOS/METEOSIX/${ano}${mes}${dia}/${ciclo}/wrf_arw_det_history_d02_${ano}${mes}${dia}_${ciclo}00.nc4' % PATH},
               },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

configurations['MOHID'] = {
    'mallas'  : 
            {'arousa'  : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/NCML/MyCoast/MOHID/arousa/MOHID_Arousa_${ano}${mes}${dia}_${ciclo}00.nc4'},
             'artabro' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/NCML/MyCoast/MOHID/artabro/MOHID_Artabro_${ano}${mes}${dia}_${ciclo}00.nc4'},
             'noia'    : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/NCML/MyCoast/MOHID/noia/MOHID_NoiaMuros_${ano}${mes}${dia}_${ciclo}00.nc4'},
             'vigo'    : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/NCML/MyCoast/MOHID/vigo/MOHID_Vigo_${ano}${mes}${dia}_${ciclo}00.nc4'},
            },
    'version' : 1     ,
    'tipo'    : 'PR',
    'offset'  : 1,
}

configurations['SWAN'] = {
    'mallas'   : 
       {'galicia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/RESULTADOS/SWAN/${ano}${mes}${dia}/${ciclo}/swan_galicia_${ano}${mes}${dia}_${ciclo}00.nc'},
        'baixas'  : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/RESULTADOS/SWAN/${ano}${mes}${dia}/${ciclo}/MyCoast_baixas_${ano}${mes}${dia}_${ciclo}00.nc4'},
       },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

if __name__ == '__main__':

    # Processing command line:
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', help='Model (WW3, ROMS,...)', type=str)
    parser.add_argument('-g', '--grid', help='Grid (atn, iberia, galicia,...)', ype=str)

    args = parser.parse_args()

    model = args.model.upper()
    grid = args.grid

    attributes = {}

    file_template = configurations[model]['mallas'][grid]['file_template']

    attributes['modelo']        = model
    attributes['malla']         = grid
    attributes['file_template'] = string.Template(file_template).substitute({'ano' : '????', 'mes' : '??', 'dia' : '??', 'ciclo' : '??'})
    attributes['date_template'] = string.Template(file_template).substitute({'ano' : '%Y', 'mes' : '%m', 'dia' : '%d', 'ciclo' : '%H'}).split('/')[-1]
    attributes['version']       = configurations[model]['version']
    attributes['tipo']          = configurations[model]['tipo']

    files = glob(attributes['file_template'])

    maximum = datetime(1900, 1, 1)

    for file_in in files:

        inicio                   = datetime.strptime(file_in.split('/')[-1], attributes['date_template'])
        maximum                   = max(inicio, maximum)
        inicio_real              = inicio + timedelta(days=configurations[model]['offset'])
        attributes['ciclo']      = inicio.strftime('%H')
        attributes['inicio']      = inicio.strftime('%Y%m%d')
        attributes['inicio_real'] = inicio_real.strftime('%Y%m%d')

        file_out = 'MyCOAST_V%(version)i_MeteoGalicia_%(modelo)s_%(malla)s_01hr_%(inicio_real)s%(ciclo)s_%(tipo)s.ncml' % attributes

        logging.info('Procesando fecha: %s' % inicio.strftime('%Y%m%d %H'))

        ncml_template = 'template.%s.%s' % (model, grid)

        f = open(ncml_template,'r')
        INPUT  = string.Template(f.read())
        f.close()

        f = open('%s/%s/%s' % (model, grid, file_out), 'w')
        resultado = INPUT.substitute(ano   = inicio.strftime('%Y'),
                                     mes   = inicio.strftime('%m'),
                                     dia   = inicio.strftime('%d'),
                                     ANO   = inicio_real.strftime('%Y'),
                                     MES   = inicio_real.strftime('%m'),
                                     DIA   = inicio_real.strftime('%d'),
                                     ciclo = inicio.strftime('%H'),
                                     )
        f.write(resultado)
        f.close()

    logging.info('Last: %s' % maximum.strftime('%Y%m%d %H%M'))

    f = open(ncml_template,'r')
    INPUT  = string.Template(f.read())
    f.close()

    f = open('%s/%s/%s' % (model, grid, 'latest.ncml'), 'w')
    resultado = INPUT.substitute(ano   = maximum.strftime('%Y'),
                                 mes   = maximum.strftime('%m'),
                                 dia   = maximum.strftime('%d'),
                                 ANO   = maximum.strftime('%Y'),
                                 MES   = maximum.strftime('%m'),
                                 DIA   = maximum.strftime('%d'),
                                 ciclo = maximum.strftime('%H'),
                                 )
    f.write(resultado)
    f.close()
