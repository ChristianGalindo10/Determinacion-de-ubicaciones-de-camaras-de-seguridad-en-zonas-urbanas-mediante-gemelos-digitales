# -*- coding: utf-8 -*-

import arcpy, datetime
arcpy.env.overwriteOutput = True

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [SelectionTool]


class SelectionTool:
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Selection Tool"
        self.description = ""
        self.prev_valores = {}

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = []
        
        capa_delitos = arcpy.Parameter(
            displayName="Capa Delitos",
            name="in_delitos_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        
        ponderacion = arcpy.Parameter(
            displayName='Ponderación Delitos',
            name='stat_fields',
            datatype='GPValueTable',
            parameterType='Required',
            direction='Input',
            enabled=False
        )

        ponderacion.parameterDependencies = [capa_delitos.name]
        ponderacion.columns = [['GPString', 'Tipo Delito', True], ['GPLong', 'Ponderación']]
        
        capa_cais = arcpy.Parameter(
            displayName="Capa CAI's",
            name="in_cais_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        
        capa_huella_urbana = arcpy.Parameter(
            displayName="Capa Huella urbana",
            name="in_huella_urbana_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
 
        capa_grilla_dane = arcpy.Parameter(
            displayName="Capa Grilla Dane",
            name="in_grilla_dane_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        
        capa_catastral = arcpy.Parameter(
            displayName="Capa Catastral",
            name="in_catastral_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        
        tiempo_analisis = arcpy.Parameter(
            displayName="Tiempo",
            name="in_tiempo",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        tiempo_analisis.filter.type = "ValueList"
        tiempo_analisis.filter.list = ["General", "Diurno", "Nocturno"]
        
        intervalo_tiempo = arcpy.Parameter(
            displayName="Unidad de tiempo",
            name="time_unit",
            datatype="GPTimeUnit",
            parameterType="Required",
            direction="Input"
        )
        
        tamanio_bin = arcpy.Parameter(
            displayName="Tamaño bin espaciotemporal",
            name="linear_unit",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input"
        )
        
        variable = arcpy.Parameter(
            displayName="Variable a analizar",
            name="in_field",
            datatype="Field",
            parameterType="Optional",
            direction="Input"
        )
        variable.parameterDependencies = [capa_delitos.name]
        variable.filter.list = ['Short', 'Long']
        
        operacion = arcpy.Parameter(
            displayName="Operación",
            name="in_operacion",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        operacion.filter.type = "ValueList"
        operacion.filter.list = ["Sum", "Mean"]
        
        patron = arcpy.Parameter(
            displayName="Patrón a analizar",
            name="in_patron",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        patron.filter.type = "ValueList"
        patron.filter.list = ["New Hot Spot", "Consecutive Hot Spot","Intensifying Hot Spot","Persistent Hot Spot","Diminishing Hot Spot", "Sporadic Hot Spot", "Oscillating Hot Spot", "Historical Hot Spot", "New Cold Spot", "Consecutive Cold Spot","Intensifying Cold Spot","Persistent Cold Spot","Diminishing Cold Spot", "Sporadic Cold Spot", "Oscillating Cold Spot", "Historical Cold Spot", "No Pattern Detected"]
        
        salida = arcpy.Parameter(
            displayName="Salida bins",
            name="out_bins_featurelayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output"
        )
        
        params = [capa_delitos, capa_cais, capa_huella_urbana, capa_grilla_dane, capa_catastral, tiempo_analisis, intervalo_tiempo, tamanio_bin, variable, ponderacion, operacion, patron,salida]
        return params
    
    def log(self, msg):
        with open(r"D:\Documents\UD\2024-3\Proyecto\area_estudio\debug_toolbox.log", "a") as f:
            f.write(f"[{datetime.datetime.now()}] {msg}\n")

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        (
            capa_delitos,
            capa_cais,
            capa_huella_urbana,
            capa_grilla_dane,
            capa_catastral,
            tiempo_analisis,
            intervalo_tiempo,
            tamanio_bin,
            variable,
            ponderacion,
            operacion,
            patron,
            salida
        ) = parameters
        if(capa_delitos.value and variable.value):
            if(not ponderacion.value):
                ruta = capa_delitos.valueAsText
                campo = "TIPO_DELITO"
                try:
                    tipos = set()
                    with arcpy.da.SearchCursor(ruta, [campo]) as cursor:
                        for row in cursor:
                            if row[0] is not None:
                                tipos.add(row[0])

                    tipos = sorted(list(tipos))
                    ponderacion.values = [[t, 0] for t in tipos]
                    ponderacion.enabled = True
                except Exception as e:
                    ponderacion.setErrorMessage(f"No se pudieron obtener tipos de delitos: {e}")
                    ponderacion.enabled = False
            ponderacion.enabled = True
        else:
            ponderacion.enabled = False
            
        if(variable.value):
            operacion.enabled = True
        else:
            operacion.enabled = False
            
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        (
            capa_delitos,
            capa_cais,
            capa_huella_urbana,
            capa_grilla_dane,
            capa_catastral,
            tiempo_analisis,
            intervalo_tiempo,
            tamanio_bin,
            variable,
            ponderacion,
            operacion,
            patron,
            salida
        ) = parameters
        return


    def execute(self, parameters, messages):
        """The source code of the tool."""
        (
            capa_delitos,
            capa_cais,
            capa_huella_urbana,
            capa_grilla_dane,
            capa_catastral,
            tiempo_analisis,
            intervalo_tiempo,
            tamanio_bin,
            variable,
            ponderacion,
            operacion,
            patron,
            salida
        ) = parameters
        
        temp_data = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\temp_data"
        temp_data2 = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\temp_data2"
        temp_data3 = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\temp_data3"
        temp_data4 = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\temp_data4"
        
        if(variable.value):
            arcpy.AddMessage("Calculando campos")
            exp = f"getPeso(!TIPO_DELITO!)"
            
            delitos = {}
            
            for i in ponderacion.value:
                delitos[i[0]] = i[1]
            
            codeblock = f"""
delitos = {delitos}

def getPeso(tipo):
    return delitos[tipo]
"""
            
            arcpy.CalculateField_management(
                in_table=capa_delitos.value,
                field=variable.value,
                expression=exp,
                expression_type="PYTHON3",
                code_block=codeblock
            )

        arcpy.AddMessage("Creando cubo")
        if tiempo_analisis.value == "General":
            ruta_cubo = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\cubo_espaciotemporal_ponderado.nc"
            emerging_hotspots = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\cubo_espaciotemporal_ponderado_EmergingHotSpotAnalysis"
            nombre = "cubo_espaciotemporal_ponderado_EmergingHotSpotAnalysis"
            arcpy.management.MakeFeatureLayer(
                in_features=capa_delitos.value,
                out_layer="SIEDCO",
            )
        elif tiempo_analisis.value == "Diurno":
            ruta_cubo = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\cubo_espaciotemporal_diurno_ponderado.nc"
            emerging_hotspots = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\cubo_espaciotemporal_diurno_ponderado_EmergingHotSpotAnalysis"
            nombre = "cubo_espaciotemporal_diurno_ponderado_EmergingHotSpotAnalysis"
            arcpy.management.MakeFeatureLayer(
                in_features=capa_delitos.value,
                out_layer="SIEDCO",
                where_clause="HORA >= 6 And HORA < 18"
            )
        elif tiempo_analisis.value == "Nocturno":
            ruta_cubo = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\cubo_espaciotemporal_nocturno_ponderado.nc"
            emerging_hotspots = r"D:\Documents\UD\2024-3\Proyecto\area_estudio\temp\temp.gdb\cubo_espaciotemporal_nocturno_ponderado_EmergingHotSpotAnalysis"
            nombre = "cubo_espaciotemporal_nocturno_ponderado_EmergingHotSpotAnalysis"
            arcpy.management.MakeFeatureLayer(
                in_features=capa_delitos.value,
                out_layer="SIEDCO",
                where_clause="HORA >= 18 Or HORA < 6"
            )
        
        summary_fields = None
        analysis_variable="COUNT"
        if(variable.value):
            summary_fields = variable.valueAsText + " " + operacion.valueAsText.upper() + " SPACE_TIME_NEIGHBORS"
            analysis_variable = variable.valueAsText + "_" +   operacion.valueAsText.upper() + "_SPACE_TIME_NEIGHBORS"
            
        arcpy.stpm.CreateSpaceTimeCube(
            in_features="SIEDCO",
            output_cube=ruta_cubo,
            time_field="DELTIEFECHAH",
            template_cube=None,
            time_step_interval=intervalo_tiempo.value,
            time_step_alignment="END_TIME",
            reference_time=None,
            distance_interval=tamanio_bin.value,
            summary_fields=summary_fields,
            aggregation_shape_type="FISHNET_GRID",
            defined_polygon_locations=None,
            location_id=None
        )
        
        arcpy.AddMessage("Realizando análisis de puntos calientes")
        arcpy.stpm.EmergingHotSpotAnalysis(
            in_cube=ruta_cubo,
            analysis_variable=analysis_variable,
            output_features=emerging_hotspots,
            neighborhood_distance=None,
            neighborhood_time_step=1,
            polygon_mask=None,
            conceptualization_of_spatial_relationships="FIXED_DISTANCE",
            number_of_neighbors=None,
            define_global_window="ENTIRE_CUBE"
        )
        
        arcpy.management.MakeFeatureLayer(
            in_features=emerging_hotspots,
            out_layer="HotSpots_Filtered",
            where_clause=f"PATTERN = '{patron.value}'"
        )
        
        arcpy.AddMessage("Realizando cruce huella urbana")
        
        arcpy.analysis.SpatialJoin(
            target_features="HotSpots_Filtered",
            join_features=capa_huella_urbana.value,
            out_feature_class=temp_data,
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_ALL",
            field_mapping=f'LOCATION "LOCATION" true true false 10 Long 0 0,First,#,{nombre},LOCATION,-1,-1;CATEGORY "CATEGORY" true true false 10 Long 0 0,First,#,{nombre},CATEGORY,-1,-1;PATTERN "PATTERN" true true false 254 Text 0 0,First,#,{nombre},PATTERN,0,253;PERC_HOT "PERC_HOT" true true false 19 Double 0 0,First,#,{nombre},PERC_HOT,-1,-1;PERC_COLD "PERC_COLD" true true false 19 Double 0 0,First,#,{nombre},PERC_COLD,-1,-1;TREND_Z "TREND_Z" true true false 19 Double 0 0,First,#,{nombre},TREND_Z,-1,-1;TREND_P "TREND_P" true true false 19 Double 0 0,First,#,{nombre},TREND_P,-1,-1;TREND_BIN "TREND_BIN" true true false 19 Double 0 0,First,#,{nombre},TREND_BIN,-1,-1;SUM_VALUE "SUM_VALUE" true true false 19 Double 0 0,First,#,{nombre},SUM_VALUE,-1,-1;MIN_VALUE "MIN_VALUE" true true false 19 Double 0 0,First,#,{nombre},MIN_VALUE,-1,-1;MAX_VALUE "MAX_VALUE" true true false 19 Double 0 0,First,#,{nombre},MAX_VALUE,-1,-1;MEAN_VALUE "MEAN_VALUE" true true false 19 Double 0 0,First,#,{nombre},MEAN_VALUE,-1,-1;STD_VALUE "STD_VALUE" true true false 19 Double 0 0,First,#,{nombre},STD_VALUE,-1,-1;MED_VALUE "MED_VALUE" true true false 19 Double 0 0,First,#,{nombre},MED_VALUE,-1,-1;Clase_Soc "Clase_Soc" true true false 50 Text 0 0,First,#,Clases_REGIONBog20Cun_dissolve,Clase_Soc,0,49;Residencia "Residencia" true true false 50 Text 0 0,First,#,Clases_REGIONBog20Cun_dissolve,Residencia,0,49;CLASE "CLASE" true true false 250 Text 0 0,First,#,Clases_REGIONBog20Cun_dissolve,CLASE,0,249',
            match_option="LARGEST_OVERLAP",
            search_radius=None,
            distance_field_name="",
            match_fields=None
        )
        
        arcpy.AddMessage("Realizando cruce Dane")
        
        arcpy.analysis.SpatialJoin(
            target_features=temp_data,
            join_features=capa_grilla_dane.value,
            out_feature_class=temp_data2,
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_ALL",
            field_mapping='LOCATION "LOCATION" true true false 4 Long 0 0,First,#,temp_data,LOCATION,-1,-1;CATEGORY "CATEGORY" true true false 4 Long 0 0,First,#,temp_data,CATEGORY,-1,-1;PATTERN "PATTERN" true true false 254 Text 0 0,First,#,temp_data,PATTERN,0,253;PERC_HOT "PERC_HOT" true true false 8 Double 0 0,First,#,temp_data,PERC_HOT,-1,-1;PERC_COLD "PERC_COLD" true true false 8 Double 0 0,First,#,temp_data,PERC_COLD,-1,-1;TREND_Z "TREND_Z" true true false 8 Double 0 0,First,#,temp_data,TREND_Z,-1,-1;TREND_P "TREND_P" true true false 8 Double 0 0,First,#,temp_data,TREND_P,-1,-1;TREND_BIN "TREND_BIN" true true false 8 Double 0 0,First,#,temp_data,TREND_BIN,-1,-1;SUM_VALUE "SUM_VALUE" true true false 8 Double 0 0,First,#,temp_data,SUM_VALUE,-1,-1;MIN_VALUE "MIN_VALUE" true true false 8 Double 0 0,First,#,temp_data,MIN_VALUE,-1,-1;MAX_VALUE "MAX_VALUE" true true false 8 Double 0 0,First,#,temp_data,MAX_VALUE,-1,-1;MEAN_VALUE "MEAN_VALUE" true true false 8 Double 0 0,First,#,temp_data,MEAN_VALUE,-1,-1;STD_VALUE "STD_VALUE" true true false 8 Double 0 0,First,#,temp_data,STD_VALUE,-1,-1;MED_VALUE "MED_VALUE" true true false 8 Double 0 0,First,#,temp_data,MED_VALUE,-1,-1;Clase_Soc "Clase_Soc" true true false 50 Text 0 0,First,#,temp_data,Clase_Soc,0,49;Residencia "Residencia" true true false 50 Text 0 0,First,#,temp_data,Residencia,0,49;CLASE "CLASE" true true false 250 Text 0 0,First,#,temp_data,CLASE,0,249;viviendas "viviendas" true true false 10 Long 0 0,First,#,N6_1K,viviendas,-1,-1;personas "personas" true true false 10 Long 0 0,First,#,N6_1K,personas,-1,-1',
            match_option="LARGEST_OVERLAP",
            search_radius=None,
            distance_field_name="",
            match_fields=None
        )
        
        arcpy.AddMessage("Realizando cruce CAI's")
        
        arcpy.analysis.Near(
            in_features=temp_data2,
            near_features=capa_cais.value,
            search_radius=None,
            location="NO_LOCATION",
            angle="NO_ANGLE",
            method="PLANAR",
            field_names="NEAR_DIST NEAR_DIST",
            distance_unit="Meters",
            match_fields=None
        )
        
        arcpy.management.MakeFeatureLayer(
            in_features=capa_catastral.value,
            out_layer="cons",
            where_clause="PreDestino = '01'"
        )
        
        arcpy.AddMessage("Realizando cruce construcciones residencial")
        
        arcpy.analysis.SummarizeWithin(
            in_polygons=temp_data2,
            in_sum_features="cons",
            out_feature_class=temp_data3,
            keep_all_polygons="KEEP_ALL",
            sum_fields=None,
            sum_shape="ADD_SHAPE_SUM",
            shape_unit="SQUAREMETERS",
            group_field=None,
            add_min_maj="NO_MIN_MAJ",
            add_group_percent="NO_PERCENT",
            out_group_table=None
        )
        
        arcpy.management.MakeFeatureLayer(
            in_features=capa_catastral.value,
            out_layer="cons",
            where_clause="PreDestino = '21' Or PreDestino = '22' Or PreDestino = '23'"
        )
        
        arcpy.AddMessage("Realizando cruce construcciones comercio")
        
        arcpy.analysis.SummarizeWithin(
            in_polygons=temp_data3,
            in_sum_features="cons",
            out_feature_class=temp_data4,
            keep_all_polygons="KEEP_ALL",
            sum_fields=None,
            sum_shape="ADD_SHAPE_SUM",
            shape_unit="SQUAREMETERS",
            group_field=None,
            add_min_maj="NO_MIN_MAJ",
            add_group_percent="NO_PERCENT",
            out_group_table=None
        )
        
        campos_a_eliminar = ["Join_Count", "TARGET_FID", "sum_Area_SQUAREMETERS", "sum_Area_SQUAREMETERS_1"]
        arcpy.management.DeleteField(
            in_table=temp_data4,
            drop_field=campos_a_eliminar
        )

        arcpy.management.AlterField(
            in_table=temp_data4,
            field="Polygon_Count",          
            new_field_name="Polygon_Count_Residencial",  
            new_field_alias="Polygon Count Residencial"
        )
        
        arcpy.management.AlterField(
            in_table=temp_data4,
            field="Polygon_Count_1",         
            new_field_name="Polygon_Count_Comercio", 
            new_field_alias="Polygon Count Comercio"
        )
        
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="MEAN_VALUE_norm",
            field_type="DOUBLE"
        )
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="personas_norm",
            field_type="DOUBLE"
        )
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="viviendas_norm",
            field_type="DOUBLE"
        )
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="cai_dist_norm",
            field_type="DOUBLE"
        )
        
        arcpy.AddMessage("Normalizando...")
        
        valores = [row[0] for row in arcpy.da.SearchCursor(temp_data4, ["MEAN_VALUE"]) if row[0] is not None]

        valor_min = min(valores)
        valor_max = max(valores)
        
        exp = ""
        if(valor_max - valor_min == 0):
            exp = "0"
        else:
            exp = f"(!MEAN_VALUE! - {valor_min}) / ({valor_max} - {valor_min})"
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="MEAN_VALUE_norm",
            expression= exp,
            expression_type="PYTHON3"
        )
        
        valores = [row[0] for row in arcpy.da.SearchCursor(temp_data4, ["personas"]) if row[0] is not None]

        valor_min = min(valores)
        valor_max = max(valores)
        
        exp = ""
        if(valor_max - valor_min == 0):
            exp = "0"
        else:
            exp = f"(!personas! - {valor_min}) / ({valor_max} - {valor_min})"
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="personas_norm",
            expression=exp,
            expression_type="PYTHON3"
        )
        
        valores = [row[0] for row in arcpy.da.SearchCursor(temp_data4, ["viviendas"]) if row[0] is not None]

        valor_min = min(valores)
        valor_max = max(valores)
        
        exp = ""
        if(valor_max - valor_min == 0):
            exp = "0"
        else:
            exp = f"(!viviendas! - {valor_min}) / ({valor_max} - {valor_min})"
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="viviendas_norm",
            expression=exp,
            expression_type="PYTHON3"
        )
        
        valores = [row[0] for row in arcpy.da.SearchCursor(temp_data4, ["NEAR_DIST"]) if row[0] is not None]

        valor_min = min(valores)
        valor_max = max(valores)
        
        if(valor_max - valor_min == 0):
            arcpy.management.CalculateField(
                in_table=temp_data4,
                field="cai_dist_norm",
                expression=f"0",
                expression_type="PYTHON3"
            )
        else:
            arcpy.management.CalculateField(
                in_table=temp_data4,
                field="cai_dist_norm",
                expression=f"(!NEAR_DIST! - {valor_min}) / ({valor_max} - {valor_min})",
                expression_type="PYTHON3"
            )
        
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="p_seguridad",
            field_type="DOUBLE"
        )
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="p_urbano",
            field_type="DOUBLE"
        )
        arcpy.management.AddField(
            in_table=temp_data4,
            field_name="p_policial",
            field_type="DOUBLE"
        )
        
        arcpy.AddMessage("Calculando modelos...")
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="p_seguridad",
            expression="(!MEAN_VALUE_norm! * 0.55) + (!personas_norm! * 0.20) + (!viviendas_norm! * 0.15) + (!cai_dist_norm! * 0.10)",
            expression_type="PYTHON3"
        )
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="p_urbano",
            expression="(!MEAN_VALUE_norm! * 0.4) + (!personas_norm! * 0.3) + (!viviendas_norm! * 0.2) + (!cai_dist_norm! * 0.10)",
            expression_type="PYTHON3"
        )
        
        arcpy.management.CalculateField(
            in_table=temp_data4,
            field="p_policial",
            expression="(!MEAN_VALUE_norm! * 0.45) + (!personas_norm! * 0.15) + (!viviendas_norm! * 0.1) + (!cai_dist_norm! * 0.30)",
            expression_type="PYTHON3"
        )
    
        arcpy.AddMessage("Finalizando...")
        
        arcpy.management.CopyFeatures(
            in_features=temp_data4,
            out_feature_class=salida.valueAsText
        )
        
        return [salida]

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
