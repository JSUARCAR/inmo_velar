diff --git a/pytest.ini b/pytest.ini
new file mode 100644
index 0000000..c8c9c75
--- /dev/null
+++ b/pytest.ini
@@ -0,0 +1,3 @@
+[pytest]
+asyncio_mode = auto
+asyncio_default_fixture_loop_scope = function
