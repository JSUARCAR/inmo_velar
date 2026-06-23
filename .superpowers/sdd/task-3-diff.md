diff --git a/tests/integration/test_repositorio_parametro.py b/tests/integration/test_repositorio_parametro.py
index 8b619f7..45ff402 100644
--- a/tests/integration/test_repositorio_parametro.py
+++ b/tests/integration/test_repositorio_parametro.py
@@ -4,10 +4,11 @@ Usa la base de datos real con datos de prueba prefijados.
 """
 
 import pytest
-from datetime import datetime
 
 from src.infraestructura.persistencia.database import db_manager
-from src.infraestructura.persistencia.repositorio_parametro_postgres import RepositorioParametroPostgres
+from src.infraestructura.persistencia.repositorio_parametro_postgres import (
+    RepositorioParametroPostgres,
+)
 from src.dominio.entidades.parametro_sistema import ParametroSistema
 
 
@@ -26,80 +27,108 @@ def setup_test_data():
     """Configura datos de prueba y los limpia después."""
     # Insertar datos de prueba
     with db_manager.obtener_conexion() as conn:
-        conn.executemany("""
-            INSERT OR REPLACE INTO PARAMETROS_SISTEMA 
+        cursor = conn.cursor()
+        cursor.executemany(
+            """
+            INSERT INTO PARAMETROS_SISTEMA 
             (NOMBRE_PARAMETRO, VALOR_PARAMETRO, TIPO_DATO, DESCRIPCION, CATEGORIA, MODIFICABLE)
-            VALUES (?, ?, ?, ?, ?, ?)
-        """, [
-            (f"{TEST_PREFIX}COMISION", "800", "INTEGER", "Test comisión", "COMISIONES", 1),
-            (f"{TEST_PREFIX}IMPUESTO", "4", "INTEGER", "Test impuesto", "IMPUESTOS", 0),
-            (f"{TEST_PREFIX}ALERTA", "30", "INTEGER", "Test alerta", "ALERTAS", 1),
-        ])
+            VALUES (%s, %s, %s, %s, %s, %s)
+        """,
+            [
+                (
+                    f"{TEST_PREFIX}COMISION",
+                    "800",
+                    "INTEGER",
+                    "Test comisión",
+                    "COMISIONES",
+                    True,
+                ),
+                (
+                    f"{TEST_PREFIX}IMPUESTO",
+                    "4",
+                    "INTEGER",
+                    "Test impuesto",
+                    "IMPUESTOS",
+                    False,
+                ),
+                (
+                    f"{TEST_PREFIX}ALERTA",
+                    "30",
+                    "INTEGER",
+                    "Test alerta",
+                    "ALERTAS",
+                    True,
+                ),
+            ],
+        )
         conn.commit()
-    
+
     yield
-    
+
     # Cleanup
     with db_manager.obtener_conexion() as conn:
-        conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'")
+        cursor = conn.cursor()
+        cursor.execute(
+            f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'"
+        )
         conn.commit()
 
 
 class TestRepositorioParametroPostgres:
     """Tests de integración para el repositorio de parámetros."""
-    
+
     def test_obtener_por_nombre(self, repositorio, setup_test_data):
         """Test: Obtener parámetro por nombre."""
         parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}COMISION")
-        
+
         assert parametro is not None
         assert parametro.valor_parametro == "800"
         assert parametro.categoria == "COMISIONES"
-    
+
     def test_obtener_por_nombre_no_existe(self, repositorio, setup_test_data):
         """Test: Obtener parámetro por nombre inexistente retorna None."""
         parametro = repositorio.obtener_por_nombre("NO_EXISTE_XYZ_999")
-        
+
         assert parametro is None
-    
+
     def test_listar_todos(self, repositorio, setup_test_data):
         """Test: Listar todos los parámetros incluye datos de prueba."""
         parametros = repositorio.listar_todos()
-        
+
         nombres = [p.nombre_parametro for p in parametros]
         assert any(TEST_PREFIX in n for n in nombres)
-    
+
     def test_listar_categorias(self, repositorio, setup_test_data):
         """Test: Listar categorías únicas."""
         categorias = repositorio.listar_categorias()
-        
+
         assert "COMISIONES" in categorias
         assert "IMPUESTOS" in categorias
         assert "ALERTAS" in categorias
-    
+
     def test_actualizar_parametro_modificable(self, repositorio, setup_test_data):
         """Test: Actualizar parámetro modificable."""
         parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}COMISION")
         parametro.valor_parametro = "900"
-        
+
         resultado = repositorio.actualizar(parametro, "test_user")
-        
+
         assert resultado is True
-        
+
         # Verificar
         actualizado = repositorio.obtener_por_id(parametro.id_parametro)
         assert actualizado.valor_parametro == "900"
-    
+
     def test_actualizar_parametro_no_modificable(self, repositorio, setup_test_data):
         """Test: Actualizar parámetro no modificable lanza PermissionError."""
         parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}IMPUESTO")
         parametro.valor_parametro = "5"
-        
+
         with pytest.raises(PermissionError) as exc_info:
             repositorio.actualizar(parametro, "test_user")
-        
+
         assert "no es modificable" in str(exc_info.value)
-    
+
     def test_crear_parametro(self, repositorio, setup_test_data):
         """Test: Crear nuevo parámetro."""
         nuevo = ParametroSistema(
@@ -108,14 +137,17 @@ class TestRepositorioParametroPostgres:
             tipo_dato="TEXT",
             descripcion="Parámetro de prueba",
             categoria="PRUEBAS",
-            modificable=1
+            modificable=True,
         )
-        
+
         creado = repositorio.crear(nuevo, "test_user")
-        
+
         assert creado.id_parametro is not None
-        
+
         # Cleanup adicional para este test
         with db_manager.obtener_conexion() as conn:
-            conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO = '{TEST_PREFIX}NUEVO'")
+            cursor = conn.cursor()
+            cursor.execute(
+                f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO = '{TEST_PREFIX}NUEVO'"
+            )
             conn.commit()
diff --git a/tests/integration/test_servicio_configuracion.py b/tests/integration/test_servicio_configuracion.py
index 93682f1..aabb23e 100644
--- a/tests/integration/test_servicio_configuracion.py
+++ b/tests/integration/test_servicio_configuracion.py
@@ -24,19 +24,26 @@ def servicio():
 def setup_test_usuario():
     """Crea usuario de prueba y lo elimina después."""
     hash_pass = hashlib.sha256("test123".encode()).hexdigest()
-    
+
     with db_manager.obtener_conexion() as conn:
-        conn.execute("""
-            INSERT OR REPLACE INTO USUARIOS (NOMBRE_USUARIO, CONTRASENA_HASH, ROL, ESTADO_USUARIO)
-            VALUES (?, ?, ?, ?)
-        """, (f"{TEST_PREFIX}usuario", hash_pass, "Asesor", 1))
+        cursor = conn.cursor()
+        cursor.execute(
+            """
+            INSERT INTO USUARIOS (NOMBRE_USUARIO, CONTRASENA_HASH, ROL, ESTADO_USUARIO)
+            VALUES (%s, %s, %s, %s)
+        """,
+            (f"{TEST_PREFIX}usuario", hash_pass, "Asesor", True),
+        )
         conn.commit()
-    
+
     yield
-    
+
     # Cleanup
     with db_manager.obtener_conexion() as conn:
-        conn.execute(f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO LIKE '{TEST_PREFIX}%'")
+        cursor = conn.cursor()
+        cursor.execute(
+            f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO LIKE '{TEST_PREFIX}%'"
+        )
         conn.commit()
 
 
@@ -45,17 +52,22 @@ def setup_test_ipc():
     """Crea IPC de prueba y lo elimina después."""
     # Usamos un año muy futuro para no interferir con datos reales
     with db_manager.obtener_conexion() as conn:
-        conn.execute("""
-            INSERT OR REPLACE INTO IPC (ANIO, VALOR_IPC, FECHA_PUBLICACION)
-            VALUES (?, ?, ?)
-        """, (2999, 850, "2999-01-15"))
+        cursor = conn.cursor()
+        cursor.execute(
+            """
+            INSERT INTO IPC (ANIO, VALOR_IPC, FECHA_PUBLICACION)
+            VALUES (%s, %s, %s)
+        """,
+            (2999, 850, "2999-01-15"),
+        )
         conn.commit()
-    
+
     yield
-    
+
     # Cleanup
     with db_manager.obtener_conexion() as conn:
-        conn.execute("DELETE FROM IPC WHERE ANIO = 2999")
+        cursor = conn.cursor()
+        cursor.execute("DELETE FROM IPC WHERE ANIO = 2999")
         conn.commit()
 
 
@@ -63,33 +75,40 @@ def setup_test_ipc():
 def setup_test_parametros():
     """Crea parámetros de prueba."""
     with db_manager.obtener_conexion() as conn:
-        conn.executemany("""
-            INSERT OR REPLACE INTO PARAMETROS_SISTEMA 
+        cursor = conn.cursor()
+        cursor.executemany(
+            """
+            INSERT INTO PARAMETROS_SISTEMA 
             (NOMBRE_PARAMETRO, VALOR_PARAMETRO, TIPO_DATO, CATEGORIA, MODIFICABLE)
-            VALUES (?, ?, ?, ?, ?)
-        """, [
-            (f"{TEST_PREFIX}PARAM_MOD", "100", "INTEGER", "PRUEBAS", 1),
-            (f"{TEST_PREFIX}PARAM_FIJO", "999", "INTEGER", "PRUEBAS", 0),
-        ])
+            VALUES (%s, %s, %s, %s, %s)
+        """,
+            [
+                (f"{TEST_PREFIX}PARAM_MOD", "100", "INTEGER", "PRUEBAS", True),
+                (f"{TEST_PREFIX}PARAM_FIJO", "999", "INTEGER", "PRUEBAS", False),
+            ],
+        )
         conn.commit()
-    
+
     yield
-    
+
     with db_manager.obtener_conexion() as conn:
-        conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'")
+        cursor = conn.cursor()
+        cursor.execute(
+            f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'"
+        )
         conn.commit()
 
 
 class TestServicioConfiguracionUsuarios:
     """Tests de integración para gestión de usuarios."""
-    
+
     def test_listar_usuarios(self, servicio, setup_test_usuario):
         """Test: Listar usuarios incluye el de prueba."""
         usuarios = servicio.listar_usuarios(incluir_inactivos=True)
-        
+
         nombres = [u.nombre_usuario for u in usuarios]
         assert any(TEST_PREFIX in n for n in nombres)
-    
+
     def test_crear_usuario(self, servicio):
         """Test: Crear nuevo usuario."""
         try:
@@ -97,17 +116,20 @@ class TestServicioConfiguracionUsuarios:
                 nombre_usuario=f"{TEST_PREFIX}nuevo",
                 contrasena="password123",
                 rol="Asesor",
-                usuario_sistema="admin"
+                usuario_sistema="admin",
             )
-            
+
             assert usuario.id_usuario is not None
             assert usuario.rol == "Asesor"
         finally:
             # Cleanup
             with db_manager.obtener_conexion() as conn:
-                conn.execute(f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = '{TEST_PREFIX}nuevo'")
+                cursor = conn.cursor()
+                cursor.execute(
+                    f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = '{TEST_PREFIX}nuevo'"
+                )
                 conn.commit()
-    
+
     def test_crear_usuario_contrasena_corta(self, servicio):
         """Test: Contraseña corta lanza ValueError."""
         with pytest.raises(ValueError) as exc_info:
@@ -115,11 +137,11 @@ class TestServicioConfiguracionUsuarios:
                 nombre_usuario=f"{TEST_PREFIX}short",
                 contrasena="123",
                 rol="Asesor",
-                usuario_sistema="admin"
+                usuario_sistema="admin",
             )
-        
+
         assert "6 caracteres" in str(exc_info.value)
-    
+
     def test_crear_usuario_rol_invalido(self, servicio):
         """Test: Rol inválido lanza ValueError."""
         with pytest.raises(ValueError) as exc_info:
@@ -127,100 +149,103 @@ class TestServicioConfiguracionUsuarios:
                 nombre_usuario=f"{TEST_PREFIX}bad_rol",
                 contrasena="password123",
                 rol="Gerente",
-                usuario_sistema="admin"
+                usuario_sistema="admin",
             )
-        
+
         assert "Rol inválido" in str(exc_info.value)
 
 
 class TestServicioConfiguracionIPC:
     """Tests de integración para gestión de IPC."""
-    
+
     def test_listar_ipc(self, servicio, setup_test_ipc):
         """Test: Listar valores IPC incluye el de prueba."""
         lista = servicio.listar_ipc()
-        
+
         anios = [i.anio for i in lista]
         assert 2999 in anios
-    
+
     def test_agregar_ipc(self, servicio):
         """Test: Agregar nuevo IPC."""
+        # Cleanup first to be safe
+        with db_manager.obtener_conexion() as conn:
+            cursor = conn.cursor()
+            cursor.execute("DELETE FROM IPC WHERE ANIO = 2997")
+            conn.commit()
+
         try:
             ipc = servicio.agregar_ipc(
-                anio=2998,
-                valor_ipc=900,
-                usuario_sistema="admin"
+                anio=2997, valor_ipc=900, usuario_sistema="admin"
             )
-            
+
             assert ipc.id_ipc is not None
             assert ipc.valor_ipc == 900
         finally:
             # Cleanup
             with db_manager.obtener_conexion() as conn:
-                conn.execute("DELETE FROM IPC WHERE ANIO = 2998")
+                cursor = conn.cursor()
+                cursor.execute("DELETE FROM IPC WHERE ANIO = 2997")
                 conn.commit()
-    
+
     def test_actualizar_ipc(self, servicio, setup_test_ipc):
         """Test: Actualizar valor IPC."""
         ipc = servicio.obtener_ipc_por_anio(2999)
-        
+
         resultado = servicio.actualizar_ipc(
-            id_ipc=ipc.id_ipc,
-            valor_ipc=875,
-            usuario_sistema="admin"
+            id_ipc=ipc.id_ipc, valor_ipc=875, usuario_sistema="admin"
         )
-        
+
         assert resultado is True
 
 
 class TestServicioConfiguracionParametros:
     """Tests de integración para gestión de parámetros."""
-    
+
     def test_listar_parametros(self, servicio, setup_test_parametros):
         """Test: Listar todos los parámetros incluye los de prueba."""
         parametros = servicio.listar_parametros()
-        
+
         nombres = [p.nombre_parametro for p in parametros]
         assert any(TEST_PREFIX in n for n in nombres)
-    
+
     def test_obtener_parametro(self, servicio, setup_test_parametros):
         """Test: Obtener parámetro por nombre."""
         parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_MOD")
-        
+
         assert parametro is not None
         assert parametro.valor_parametro == "100"
-    
+
     def test_obtener_valor_parametro(self, servicio, setup_test_parametros):
         """Test: Obtener valor de parámetro convertido."""
         valor = servicio.obtener_valor_parametro(f"{TEST_PREFIX}PARAM_MOD")
-        
+
         assert valor == 100
-    
+
     def test_obtener_valor_parametro_no_existe(self, servicio):
         """Test: Obtener valor de parámetro inexistente retorna default."""
         valor = servicio.obtener_valor_parametro("NO_EXISTE_XYZ_999", default=50)
-        
+
         assert valor == 50
-    
+
     def test_actualizar_parametro_modificable(self, servicio, setup_test_parametros):
         """Test: Actualizar parámetro modificable."""
         parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_MOD")
-        
+
         resultado = servicio.actualizar_parametro(
             id_parametro=parametro.id_parametro,
             nuevo_valor="200",
-            usuario_sistema="admin"
+            usuario_sistema="admin",
         )
-        
+
         assert resultado is True
-    
+
     def test_actualizar_parametro_no_modificable(self, servicio, setup_test_parametros):
         """Test: Actualizar parámetro no modificable lanza PermissionError."""
         parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_FIJO")
-        
+
         with pytest.raises(PermissionError):
             servicio.actualizar_parametro(
                 id_parametro=parametro.id_parametro,
                 nuevo_valor="1000",
-                usuario_sistema="admin"
+                usuario_sistema="admin",
             )
