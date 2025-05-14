bl_info = {
    "name": "CharpstAR Tools",
    "author": "Gabriel Gomides Surjus",
    "version": (1, 0, 0),
    "blender": (4, 2, 9),
    "location": "View3D > Sidebar > CharpstAR",
    "description": "Addon with tools for centering, renaming and other operations.",
    "warning": "",
    "category": "Object",
}

import bpy
import bmesh
from .easybpy import *
from bpy.props import StringProperty

# Operador que renomeia o objeto ativo com o texto digitado no painel
class OBJECT_OT_create_empty(bpy.types.Operator):
    bl_idname = "object.create_empty"
    bl_label = "Create Empty"
    bl_description = "create an empty one with the given ID name and parent the objects in it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Pega o nome a partir da propriedade customizada armazenada na cena
        numeroID = context.scene.article_id

        # Cria um empty do tipo 'PLAIN_AXES' na posição (0, 0, 0)
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))

        # Obtém o empty recém-criado, que é o objeto ativo
        empty_obj = bpy.context.active_object

        # Altera o nome do objeto imediatamente
        empty_obj.name = numeroID

        #seleciona todas as meshes
        select_all_meshes()

        #seleciona e ativa o parent
        empty_obj.select_set(True)
        bpy.context.view_layer.objects.active = empty_obj

        #cria o parent no objeto ativo
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        return {'FINISHED'}

#Renomeia a malha com o nome do objeto
class OBJECT_OT_rename_mesh(bpy.types.Operator):
    bl_idname = "object.rename_mesh"
    bl_label = "Rename Meshes"
    bl_description = "rename the meshes with the name of their objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #seleciona todas as meshes
        select_all_meshes()

        # Obtém os objetos selecionados na cena
        selected_objects = bpy.context.selected_objects

        # Percorre cada objeto selecionado
        for obj in selected_objects:
            # Verifica se o objeto é uma mesh
            if obj.type == 'MESH':
                # Renomeia a mesh (dados) para ter o mesmo nome do objeto
                obj.data.name = obj.name
        return {'FINISHED'}

 #ativa o backface culling  
class OBJECT_OT_activates_backface_culling(bpy.types.Operator):
    bl_idname = "object.activates_backface_culling"
    bl_label = "Activates Backface Culling"
    bl_description = "activates backface culling on all materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Itera por todos os materiais do arquivo
        for mat in bpy.data.materials:
            # Ativa a opção de backface culling para cada material
            mat.use_backface_culling = True
        return {'FINISHED'}
    
 #Renomeia material  
class OBJECT_OT_rename_materials(bpy.types.Operator):
    bl_idname = "object.rename_materials"
    bl_label = "Rename Materials"
    bl_description = "renames all materials materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        counter = 1
        for obj in bpy.data.objects:
            # Verifica se o objeto é do tipo MESH
            if obj.type == 'MESH':
                # Itera por todos os slots de material do objeto
                for slot in obj.material_slots:
                    if slot.material is not None:  # Verifica se há material atribuído
                        slot.material.name = f"{counter}_{obj.name}"
                        counter += 1
        return {'FINISHED'}

# Add suffix _Seamless
class OBJECT_OT_add_suffix_seamless(bpy.types.Operator):
    bl_idname = "object.add_suffix_seamless"
    bl_label = "suffix Seamless"
    bl_description = "Replace _PBR with _Seamless or add _Seamless"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material is not None:
                        current_name = slot.material.name
                        if current_name.endswith('_PBR'):
                            slot.material.name = current_name[:-4] + '_Seamless'
                        elif not current_name.endswith('_Seamless') and not current_name.endswith('_'):
                            slot.material.name = current_name + '_Seamless'
        return {'FINISHED'}

# Add suffix _PBR
class OBJECT_OT_add_suffix_pbr(bpy.types.Operator):
    bl_idname = "object.add_suffix_pbr"
    bl_label = "suffix PBR"
    bl_description = "Replace _Seamless with _PBR or add _PBR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material is not None:
                        current_name = slot.material.name
                        if current_name.endswith('_Seamless'):
                            slot.material.name = current_name[:-9] + '_PBR'
                        elif not current_name.endswith('_PBR') and not current_name.endswith('_'):
                            slot.material.name = current_name + '_PBR'
        return {'FINISHED'}

#organiza o pivo para baixo do objeto e depois manda para o centro domundo
class OBJECT_OT_objects_to_world_origin(bpy.types.Operator):
    bl_idname = "object.objects_to_world_origin"
    bl_label = "Objects to World Origin"
    bl_description = "calculates the base of objects, centers them in the center of the world"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Salva a posição atual do 3D Cursor
        posicao_cursor = bpy.context.scene.cursor.location.copy()

        # Seleciona todas as meshes na cena
        select_all_meshes()

        # Obtém a lista dos objetos selecionados
        selected_objects = bpy.context.selected_objects

        # Duplica os objetos selecionados
        bpy.ops.object.duplicate()

        # Após a duplicação, obtém os novos objetos duplicados
        duplicated_objects = bpy.context.selected_objects

        if duplicated_objects:
            # Define o primeiro objeto duplicado como ativo
            bpy.context.view_layer.objects.active = duplicated_objects[0]
            # Junta os objetos duplicados em um único objeto
            bpy.ops.object.join()

        # Recupera o objeto ativo (resultado da união)
        obj = bpy.context.view_layer.objects.active

        if obj and obj.type == 'MESH':
            # Cria um bmesh a partir dos dados da malha do objeto
            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.transform(obj.matrix_world)
            
            # Calcula o menor valor de Z entre os vértices (base do objeto)
            min_z = min((v.co.z for v in bm.verts), default=obj.location.z)
            bm.free()
            
            # Reposiciona o 3D Cursor para o ponto base do objeto, mantendo X e Y
            bpy.context.scene.cursor.location = (obj.location.x, obj.location.y, min_z)
            
            # Define novo nome para o objeto e sua mesh
            novo_nome = "Ref_Temp"
            obj.name = novo_nome
            obj.data.name = novo_nome + "_Mesh"
            
            # Deleta o objeto temporário (já que foi usado apenas para calcular a posição)
            bpy.ops.object.delete(use_global=False)

        # Seleciona novamente todas as meshes que permanecem na cena
        select_all_meshes()    

        # Define a origem dos objetos selecionados para a posição do 3D Cursor
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Move todos os objetos selecionados para o centro do mundo (0,0,0)
        for obj in bpy.context.selected_objects:
            obj.location = (0, 0, 0)
            
        # Restaura a posição original do 3D Cursor
        bpy.context.scene.cursor.location = posicao_cursor

        return {'FINISHED'}
    
# Purge
class OBJECT_OT_purge(bpy.types.Operator):
    bl_idname = "object.purge"
    bl_label = "Clean .Blend"
    bl_description = "eliminates blocks of data that are not being used (such as unreferenced materials, textures and meshes)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        return {'FINISHED'}

#-----------------------------------------------------------------------------------------------------------

# Painel na interface do Blender onde será exibido o campo de texto e o botão de renomear
class VIEW3D_PT_main_panel(bpy.types.Panel):
    bl_label = "CharpstAR Tools"
    bl_idname = "VIEW3D_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CharpstAR'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Article Settings Box
        box_article = layout.box()
        box_article.label(text="Article Settings", icon='INFO')
        box_article.prop(scene, "article_id", text="Article ID")
        box_article.operator("object.create_empty", text="Create Empty", icon='PLUS')

        layout.separator()

        # Object Operations Box
        box_object = layout.box()
        box_object.label(text="Object Operations", icon='OBJECT_DATA')
        box_object.operator("OBJECT_OT_objects_to_world_origin", text="Move to World Origin", icon='HOME')

        layout.separator()

        # Mesh Tools Box
        box_mesh = layout.box()
        box_mesh.label(text="Mesh Tools", icon='MESH_DATA')
        box_mesh.operator("object.rename_mesh", text="Rename Mesh", icon='OUTLINER_DATA_MESH')
        box_mesh.operator("object.activates_backface_culling", text="Activate Backface Culling", icon='RESTRICT_VIEW_OFF')

        layout.separator()

        # Material Tools Box
        box_material = layout.box()
        box_material.label(text="Material Tools", icon='MATERIAL')
        box_material.operator("object.rename_materials", text="Rename Materials", icon='FILE_TEXT')
        row = box_material.row(align=True)
        row.operator("object.add_suffix_seamless", text="Suffix Seamless", icon='MOD_BOOLEAN')
        row.operator("object.add_suffix_pbr", text="Suffix PBR", icon='RENDER_STILL')

        layout.separator()

        # Purge Button with Alert
        purge_btn = layout.operator("object.purge", text="Clean .Blend", icon='ERROR')
        purge_btn.alert = True


        
        

# Função de registro: registra as classes e adiciona a propriedade customizada à cena
def register():
    bpy.utils.register_class(OBJECT_OT_create_empty)
    bpy.utils.register_class(OBJECT_OT_rename_mesh)
    bpy.utils.register_class(OBJECT_OT_activates_backface_culling)
    bpy.utils.register_class(OBJECT_OT_rename_materials)
    bpy.utils.register_class(OBJECT_OT_add_suffix_seamless)
    bpy.utils.register_class(OBJECT_OT_add_suffix_pbr)
    bpy.utils.register_class(OBJECT_OT_objects_to_world_origin)
    bpy.utils.register_class(OBJECT_OT_purge)
    bpy.utils.register_class(VIEW3D_PT_main_panel)
    bpy.types.Scene.article_id = StringProperty(
        name="Novo Nome",
        description="enter an ID"
    )

# Função de desregistro: remove as classes e a propriedade customizada
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_create_empty)
    bpy.utils.unregister_class(OBJECT_OT_rename_mesh)
    bpy.utils.unregister_class(OBJECT_OT_activates_backface_culling)
    bpy.utils.unregister_class(OBJECT_OT_rename_materials)
    bpy.utils.unregister_class(OBJECT_OT_add_suffix_seamless)
    bpy.utils.unregister_class(OBJECT_OT_add_suffix_pbr)
    bpy.utils.unregister_class(OBJECT_OT_objects_to_world_origin)
    bpy.utils.unregister_class(OBJECT_OT_purge)
    bpy.utils.unregister_class(VIEW3D_PT_main_panel)
    del bpy.types.Scene.article_id

if __name__ == "__main__":
    register()
