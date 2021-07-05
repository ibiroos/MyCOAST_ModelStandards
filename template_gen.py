#!/bin/env python
# -*- coding: utf-8 -*-

import string
from glob import glob
from datetime import datetime, timedelta

import argparse

import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

configuraciones = {}

PATH = '/mnt/netapp_ext2/Store_Meteo/'

configuraciones['WW3'] = {
    'mallas'  : 
            {'atn'     : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_atn_${ano}${mes}${dia}_${ciclo}00.nc'}    , 
             'iberia'  : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_iberico_${ano}${mes}${dia}_${ciclo}00.nc'}, 
             'galicia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/THREDDS/${ano}${mes}${dia}/${ciclo}/ww3_galicia_${ano}${mes}${dia}_${ciclo}00.nc'},
            },
    'version' : 1     ,
    'tipo'    : 'ANPR',
    'offset'  : 0,
}

configuraciones['ROMS'] = {
    'mallas'   : {'iberia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/PRODUCTOS/ROMS_GEOPOT/${ano}${mes}${dia}/${ciclo}/roms_002_${ano}${mes}${dia}_${ciclo}00.nc'},
                 },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

configuraciones['WRF'] = {
    'mallas'   : 
               {'galicia' : {'file_template' : '%s/OP/DATOS/PRODUCTOS/METEOSIX/${ano}${mes}${dia}/${ciclo}/wrf_arw_det_history_d03_${ano}${mes}${dia}_${ciclo}00.nc4' % PATH},
                'iberia'  : {'file_template' : '%s/OP/DATOS/PRODUCTOS/METEOSIX/${ano}${mes}${dia}/${ciclo}/wrf_arw_det_history_d02_${ano}${mes}${dia}_${ciclo}00.nc4' % PATH},
               },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

configuraciones['MOHID'] = {
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

configuraciones['SWAN'] = {
    'mallas'   : 
       {'galicia' : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/RESULTADOS/SWAN/${ano}${mes}${dia}/${ciclo}/swan_galicia_${ano}${mes}${dia}_${ciclo}00.nc'},
        'baixas'  : {'file_template' : '/mnt/netapp_ext2/Store_Meteo/OP/DATOS/RESULTADOS/SWAN/${ano}${mes}${dia}/${ciclo}/MyCoast_baixas_${ano}${mes}${dia}_${ciclo}00.nc4'},
       },
    'version' : 1      ,
    'tipo'    : 'PR'   ,
    'offset'  : 0,
}

if __name__=='__main__':

    # Procesado de la linea de comandos:
    parser = argparse.ArgumentParser()
    parser.add_argument('-m','--modelo',help='Modelo (WW3, ROMS)',type=str)
    parser.add_argument('-g','--grid',help='Malla (atn, iberia, galicia, )',type=str)

    args   = parser.parse_args()

    modelo = args.modelo.upper()
    malla  = args.grid

    atributos = {}

    file_template = configuraciones[modelo]['mallas'][malla]['file_template']

    atributos['modelo']        = modelo
    atributos['malla']         = malla
    atributos['file_template'] = string.Template(file_template).substitute({'ano' : '????', 'mes' : '??', 'dia' : '??', 'ciclo' : '??'})
    atributos['date_template'] = string.Template(file_template).substitute({'ano' : '%Y', 'mes' : '%m', 'dia' : '%d', 'ciclo' : '%H'}).split('/')[-1]
    atributos['version']       = configuraciones[modelo]['version']
    atributos['tipo']          = configuraciones[modelo]['tipo']

    ficheros = glob(atributos['file_template'])

    maximo   = datetime(1900,1,1)

    for fichero_in in ficheros:

        inicio                   = datetime.strptime(fichero_in.split('/')[-1], atributos['date_template'])
        maximo                   = max(inicio, maximo)
        inicio_real              = inicio + timedelta(days=configuraciones[modelo]['offset'])
        atributos['ciclo' ]      = inicio.strftime('%H')    
        atributos['inicio']      = inicio.strftime('%Y%m%d')
        atributos['inicio_real'] = inicio_real.strftime('%Y%m%d')

        fichero_out = 'MyCOAST_V%(version)i_MeteoGalicia_%(modelo)s_%(malla)s_01hr_%(inicio_real)s%(ciclo)s_%(tipo)s.ncml' % atributos

        logging.info('Procesando fecha: %s' % inicio.strftime('%Y%m%d %H'))

        ncml_template = 'template.%s.%s' % (modelo, malla)

        f = open(ncml_template,'r')
        INPUT  = string.Template(f.read())
        f.close()

        f = open('%s/%s/%s' % (modelo, malla, fichero_out),'w')
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

    logging.info('Last: %s' % maximo.strftime('%Y%m%d %H%M'))

    f = open(ncml_template,'r')
    INPUT  = string.Template(f.read())
    f.close()

    f = open('%s/%s/%s' % (modelo, malla, 'latest.ncml'),'w')
    resultado = INPUT.substitute(ano   = maximo.strftime('%Y'),
                                 mes   = maximo.strftime('%m'),
                                 dia   = maximo.strftime('%d'),
                                 ANO   = maximo.strftime('%Y'),
                                 MES   = maximo.strftime('%m'),
                                 DIA   = maximo.strftime('%d'),
                                 ciclo = maximo.strftime('%H'),
                                 )
    f.write(resultado)
    f.close()
