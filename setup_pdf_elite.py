"""
Script de Setup para el Módulo PDF de Élite
============================================
Crea la estructura completa de directorios y archivos base
para el sistema de generación PDF élite.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import List, Dict


class PDFEliteSetup:
    """Configurador del módulo PDF élite"""
    
    BASE_DIR = Path("src/infraestructura/servicios/pdf_elite")
    
    STRUCTURE: Dict[str, List[str]] = {
        "core": [
            "__init__.py",
            "base_generator.py",
            "reportlab_generator.py",
            "config.py"
        ],
        "components": [
            "__init__.py",
            "headers.py",
            "footers.py",
            "tables.py",
            "charts.py",
            "watermarks.py",
            "signatures.py"
        ],
        "templates": [
            "__init__.py",
            "base_template.py",
            "contrato_template.py",
            "certificado_template.py",
            "informe_template.py",
            "estado_cuenta_elite.py"
        ],
        "utils": [
            "__init__.py",
            "qr_generator.py",
            "barcode_generator.py",
            "chart_converter.py",
            "validators.py"
        ],
        "styles": [
            "__init__.py",
            "colors.py",
            "fonts.py",
            "themes.py"
        ]
    }
    
    def __init__(self):
        self.created_dirs: List[Path] = []
        self.created_files: List[Path] = []
    
    def create_structure(self) -> None:
        """Crea la estructura completa de directorios"""
        print("=" * 70)
        print("🚀 INICIO DE SETUP - MÓDULO PDF ÉLITE")
        print("=" * 70)
        
        # Crear directorio base
        self._create_directory(self.BASE_DIR)
        
        # Crear archivo __init__.py principal
        main_init = self.BASE_DIR / "__init__.py"
        self._create_init_file(
            main_init,
            '"""Módulo PDF de Élite para Inmobiliaria Velar"""\n\n'
            '__version__ = "1.0.0"\n'
            '__author__ = "Inmobiliaria Velar SAS"\n'
        )
        
        # Crear subdirectorios y archivos
        for subdir_name, files in self.STRUCTURE.items():
            subdir_path = self.BASE_DIR / subdir_name
            self._create_directory(subdir_path)
            
            for filename in files:
                filepath = subdir_path / filename
                
                if filename == "__init__.py":
                    self._create_init_file(
                        filepath,
                        f'"""{subdir_name.title()} module for PDF Elite system"""\n'
                    )
                else:
                    self._create_module_file(filepath, subdir_name, filename)
        
        # Crear directorio de tests
        self._create_test_structure()
        
        # Crear directorio de fonts
        self._create_fonts_directory()
        
        # Resumen
        self._print_summary()
    
    def _create_directory(self, path: Path) -> None:
        """Crea un directorio si no existe"""
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(path)
            print(f"✓ Directorio creado: {path}")
        else:
            print(f"○ Ya existe: {path}")
    
    def _create_init_file(self, path: Path, content: str) -> None:
        """Crea archivo __init__.py con contenido"""
        if not path.exists():
            path.write_text(content, encoding='utf-8')
            self.created_files.append(path)
            print(f"  ✓ Archivo creado: {path.name}")
    
    def _create_module_file(self, path: Path, module: str, filename: str) -> None:
        """Crea archivo de módulo con docstring base"""
        if not path.exists():
            module_name = filename.replace('.py', '').replace('_', ' ').title()
            content = f'"""\n{module_name}\n{"=" * len(module_name)}\n'
            content += f'Módulo: {module}\n'
            content += f'Propósito: [Pendiente implementación]\n'
            content += f'"""\n\n'
            content += 'from typing import Any, Dict, List, Optional\n\n'
            content += '# TODO: Implementar funcionalidad\n'
            
            path.write_text(content, encoding='utf-8')
            self.created_files.append(path)
            print(f"  ✓ Archivo creado: {path.name}")
    
    def _create_test_structure(self) -> None:
        """Crea estructura de tests"""
        test_dir = Path("tests/pdf_elite")
        self._create_directory(test_dir)
        
        test_files = [
            "__init__.py",
            "test_config.py",
            "test_components.py",
            "test_templates.py",
            "test_generators.py",
            "test_utils.py",
            "test_integration.py"
        ]
        
        for test_file in test_files:
            test_path = test_dir / test_file
            if not test_path.exists():
                if test_file == "__init__.py":
                    content = '"""Tests for PDF Elite module"""\n'
                else:
                    content = f'"""\nTests for {test_file.replace("test_", "").replace(".py", "")}\n"""\n'
                    content += 'import pytest\n\n'
                    content += '# TODO: Implement tests\n'
                
                test_path.write_text(content, encoding='utf-8')
                self.created_files.append(test_path)
                print(f"  ✓ Test creado: {test_file}")
    
    def _create_fonts_directory(self) -> None:
        """Crea directorio para fuentes personalizadas"""
        fonts_dir = Path("assets/fonts")
        self._create_directory(fonts_dir)
        
        # Crear archivo README
        readme = fonts_dir / "README.md"
        if not readme.exists():
            content = """# Fuentes Personalizadas para PDFs

## Instrucciones

Coloca aquí las fuentes TrueType (.ttf) que desees usar en los documentos PDF.

### Fuentes Recomendadas:
- Roboto (Google Fonts)
- Montserrat (Google Fonts)
- Open Sans (Google Fonts)

### Uso:
Las fuentes se registran automáticamente en el sistema PDF.
"""
            readme.write_text(content, encoding='utf-8')
            print(f"  ✓ README creado: {readme.name}")
    
    def _print_summary(self) -> None:
        """Imprime resumen de la instalación"""
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print(f"📁 Directorios creados: {len(self.created_dirs)}")
        print(f"📄 Archivos creados: {len(self.created_files)}")
        print("\n📊 Estructura:")
        
        for dir in sorted(self.created_dirs):
            relative = dir.relative_to(Path.cwd())
            print(f"  {relative}/")
        
        print("\n🎯 Próximos pasos:")
        print("  1. Implementar core/config.py")
        print("  2. Implementar componentes base")
        print("  3. Crear templates de documentos")
        print("  4. Ejecutar tests")
        print("=" * 70)


def main():
    """Función principal"""
    setup = PDFEliteSetup()
    setup.create_structure()


if __name__ == "__main__":
    main()
