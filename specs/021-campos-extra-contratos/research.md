# Research Phase: campos-extra-contratos

- **Unknowns Identified**: None. The project constitution and architecture strictly define the tech stack and patterns (Reflex, PostgreSQL, Clean Architecture).
- **Decisions**:
  - **Stack**: Reflex + Python + PostgreSQL.
  - **Pattern**: Clean Architecture (Dominio, Aplicación, Infraestructura, Presentación).
  - **Data Integration**:
    - Use `%s` for PostgreSQL placeholders.
    - Use standard `rx.input` for the video URL.
    - Use `rx.select` for the ComboBox of active advisors.
  - **URL Validation**: Done using Pydantic in the Application layer (DTO).
