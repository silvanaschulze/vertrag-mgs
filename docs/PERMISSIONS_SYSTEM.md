# Sistema de Permissões e Roles / Berechtigungssystem und Rollen

**Data / Datum**: 27.11.2025  
**Status**: Implementiert / Implementado

---

## 📋 Resumo das Alterações / Zusammenfassung der Änderungen

### DE: Deutsche Zusammenfassung

Das Berechtigungssystem wurde vollständig überarbeitet und erweitert, um eine granulare Zugriffskontrolle basierend auf **Rollen (Roles)**, **Zugriffsstufen (Access Levels)**, **Bereichen (Departments)** und **Teams** zu ermöglichen.

**Hauptänderungen:**

1. **Neue Benutzerrollen (UserRole)**: 7 spezifische Rollen ersetzt die alten 3 Rollen (USER/MANAGER/ADMIN)
2. **Zugriffsstufen (AccessLevel)**: 6 hierarchische Stufen (1-6) für differenzierte Berechtigungen
3. **Organisatorische Felder**: `department` und `team` im User- und Contract-Modell
4. **Granulare Berechtigungsfunktionen**: Neue Funktionen für Vertrags- und Benutzerverwaltung
5. **Standardprofile (PERFIS_PADRAO)**: Vordefinierte Rollenkombinationen für typische Anwendungsfälle

---

### PT: Resumo em Português

O sistema de permissões foi completamente refatorado e expandido para permitir controle de acesso granular baseado em **Papéis (Roles)**, **Níveis de Acesso (Access Levels)**, **Departamentos (Departments)** e **Times (Teams)**.

**Principais mudanças:**

1. **Novos papéis de usuário (UserRole)**: 7 papéis específicos substituíram os 3 antigos (USER/MANAGER/ADMIN)
2. **Níveis de acesso (AccessLevel)**: 6 níveis hierárquicos (1-6) para permissões diferenciadas
3. **Campos organizacionais**: `department` e `team` nos modelos User e Contract
4.  **Funções de permissão granulares**: Novas funções para gestão de contratos e usuários
5. **Perfis padrão (PERFIS_PADRAO)**: Combinações de papéis pré-definidas para casos típicos

---

##  Novos Papéis (Roles) / Neue Rollen

| Role | Valor | Nível Padrão | DE Beschreibung | PT Descrição |
|------|-------|--------------|-----------------|--------------|
| `SYSTEM_ADMIN` | "system_admin" | 6 | Technischer Systemadministrator mit Vollzugriff | Admin técnico com acesso completo |
| `DIRECTOR` | "director" | 5 | Geschäftsführung mit unternehmensweitem Zugriff | Diretoria com acesso em toda empresa |
| `DEPARTMENT_ADM` | "department_adm" | 4 | Bereichsleiter mit vollen Admin-Rechten im Bereich | Gestor com direitos administrativos completos no departamento |
| `DEPARTMENT_USER` | "department_user" | 3 | Bereichsleiter mit eingeschränkten Funktionen | Gestor com funções restritas no departamento |
| `TEAM_LEAD` | "team_lead" | 2 | Teamleiter | Líder de time |
| `STAFF` | "staff" | 1-2 | Mitarbeiter | Colaborador |
| `READ_ONLY` | "read_only" | 1 | Nur Lesezugriff | Somente leitura |

---

## Níveis de Acesso (AccessLevel) / Zugriffsstufen

| Nível | Nome | DE Beschreibung | PT Descrição |
|-------|------|-----------------|--------------|
| **6** | SYSTEM_ADMIN | Technischer Vollzugriff: Konfiguration, Integrationen, Sicherheit, Logs, Backups | Acesso técnico completo: configurações, integrações, segurança, logs, backups |
| **5** | DIRECTOR | Unternehmensweiter Zugriff auf alle Verträge und Reports | Acesso a todos os contratos e relatórios da empresa |
| **4** | DEPARTMENT_ADM | Volle Bereichsrechte: Verträge, Benutzer, vollständige Reports im Bereich | Direitos completos do departamento: contratos, usuários, relatórios completos |
| **3** | DEPARTMENT_USER | Bereichsverträge sehen/genehmigen, eingeschränkte Reports (ohne Beträge) | Ver/aprovar contratos do departamento, relatórios restritos (sem valores) |
| **2** | TEAM | Alle Verträge des eigenen Teams sehen/bearbeiten | Ver/editar todos contratos do próprio time |
| **1** | BASIS | Nur eigene Verträge sehen | Ver apenas contratos próprios |

---

##  Departamentos e Times / Bereiche und Teams

### Departamentos (Bereiche)
- `Geschäftsführung`
- `Personal Organization und Finanzen`
- `Technischer Bereich`
- `IT und Datenschutz`

### Times (Teams)
- `Personal und Organization`
- `Finanzen und Rechnungswesen`
- `Bauen und Sanieren`
- `Gebäudewirtschaft`
- `Informationstechnologie`
- `PR`

---

##  Principais Funções de Permissão / Hauptberechtigungsfunktionen

### Contratos / Verträge

#### `can_view_contract(user, contract) -> bool`
**DE**: Prüft, ob der Benutzer den Vertrag sehen darf.  
**PT**: Verifica se o usuário pode visualizar o contrato.

**Lógica**:
- Level 6 (SYSTEM_ADMIN): Alles / Tudo
- Level 5 (DIRECTOR): Alles / Tudo
- Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
- Level 3 (DEPARTMENT_USER): Bereichsverträge / Contratos do departamento
- Level 2 (TEAM): Team-Verträge + eigene / Contratos do time + próprios
- Level 1 (BASIS): Nur eigene / Apenas próprios

---

#### `can_edit_contract(user, contract) -> bool`
**DE**: Prüft, ob der Benutzer den Vertrag bearbeiten darf.  
**PT**: Verifica se o usuário pode editar o contrato.

**Lógica**:
- Level 6-5: Alles / Tudo
- Level 4-3: Bereichsverträge / Contratos do departamento
- TEAM_LEAD: Team-Verträge / Contratos do time
- STAFF Level 2: Team-Verträge + eigene / Contratos do time + próprios
- STAFF Level 1: Nur eigene / Apenas próprios
- READ_ONLY: Nichts / Nada

---

#### `can_delete_contract(user, contract) -> bool`
**DE**: Prüft, ob der Benutzer den Vertrag löschen darf.  
**PT**: Verifica se o usuário pode deletar o contrato.

**Lógica**:
- Level 6-5: Alles / Tudo
- Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
- Andere: Nichts / Outros: Nada

---

#### `can_approve_contract(user, contract) -> bool`
**DE**: Prüft, ob der Benutzer den Vertrag genehmigen darf.  
**PT**: Verifica se o usuário pode aprovar o contrato.

**Lógica**:
- Level 6-5: Alles / Tudo
- Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
- Level 3 (DEPARTMENT_USER): Bereichsverträge / Contratos do departamento
- TEAM_LEAD: Team-Verträge / Contratos do time

---

### Usuários / Benutzer

#### `can_manage_users(user, target_user) -> bool`
**DE**: Prüft, ob der Benutzer andere Benutzer verwalten darf.  
**PT**: Verifica se o usuário pode gerenciar outros usuários.

**Lógica**:
- Level 6-5: Alle Benutzer / Todos usuários
- Level 4 (DEPARTMENT_ADM): Bereichsbenutzer / Usuários do departamento
- Level 3 (DEPARTMENT_USER): Bereichsbenutzer mit Level ≤ 3 / Usuários do departamento com nível ≤ 3

---

#### `can_set_user_role(user, target_role, target_level) -> bool`
**DE**: Prüft, ob der Benutzer eine bestimmte Rolle und Level vergeben darf.  
**PT**: Verifica se o usuário pode definir uma função e nível específicos.

**Lógica**:
- Level 6: Alle Rollen / Todas funções
- Level 5: Bis Level 5 / Até nível 5
- Level 4: Bis Level 4 / Até nível 4
- Level 3: Bis Level 3 / Até nível 3

---

#### `can_access_reports(user, include_financials) -> bool`
**DE**: Prüft, ob der Benutzer auf Reports zugreifen darf.  
**PT**: Verifica se o usuário pode acessar relatórios.

**Lógica**:
- Level 6-5: Alle Reports / Todos relatórios
- Level 4 (DEPARTMENT_ADM): Volle Bereichsreports / Relatórios completos do departamento
- Level 3 (DEPARTMENT_USER): Eingeschränkte Reports ohne Beträge / Relatórios restritos sem valores

---

## 👥 Perfis Padrão / Standardprofile (PERFIS_PADRAO)

O dicionário `PERFIS_PADRAO` em `permissions.py` contém combinações pré-definidas:

```python
PERFIS_PADRAO = {
    "Geschäftsführung": {
        "role": UserRole.DIRECTOR,
        "access_level": AccessLevel.LEVEL_5,
        "department": "Geschäftsführung",
        "team": None
    },
    "Leiter_Personal_Organization_Finanzen": {
        "role": UserRole.DEPARTMENT_ADM,
        "access_level": AccessLevel.LEVEL_4,
        "department": "Personal Organization und Finanzen",
        "team": None
    },
    "Systemadministrator_TI": {
        "role": UserRole.SYSTEM_ADMIN,
        "access_level": AccessLevel.LEVEL_6,
        "department": "IT und Datenschutz",
        "team": "Informationstechnologie"
    },
    # ... mais perfis
}
```

---

## 🔄 Mudanças nos Modelos / Modelländerungen

### User Model (`backend/app/models/user.py`)

**Novos campos / Neue Felder**:
```python
team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
access_level: Mapped[int] = mapped_column(Integer, default=AccessLevel.LEVEL_1, nullable=False)
```

**Novos métodos / Neue Methoden**:
```python
def is_system_admin(self) -> bool
def is_director(self) -> bool
def is_department_leader(self) -> bool
def has_department_access(self) -> bool
def is_read_only(self) -> bool
```

---

### Contract Model (`backend/app/models/contract.py`)

**Novos campos / Neue Felder**:
```python
department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
```

---

##  Mudanças nos Schemas / Schema-Änderungen

### User Schemas (`backend/app/schemas/user.py`)

**Atualizações / Aktualisierungen**:
- Novo enum `AccessLevel` (IntEnum)
- Enum `UserRole` atualizado com 7 novos papéis
- `UserBase` agora inclui: `department`, `team`, `access_level`
- `UserUpdate` atualizado com os mesmos campos
- Validator `validate_superuser` ajustado para SYSTEM_ADMIN e DIRECTOR

---

##  Funções Deprecadas / Veraltete Funktionen

As seguintes funções foram mantidas para compatibilidade mas estão **DEPRECATED**:

```python
require_admin(user)  # Use: require_system_admin() ou require_director()
require_manager_or_admin(user)  # Use: require_min_access_level(user, 3)
can_edit_contracts(user)  # Use: can_edit_contract(user, contract)
can_delete_contracts(user)  # Use: can_delete_contract(user, contract)
```

---

##  Próximos Passos / Nächste Schritte

### 1. Migration de Banco de Dados / Datenbankmigration

É necessário criar uma migração Alembic para adicionar os novos campos:

```bash
# DE: Alembic-Migration erstellen
# PT: Criar migração Alembic
alembic revision --autogenerate -m "add_access_level_team_and_new_roles"
alembic upgrade head
```

**Campos a migrar / Zu migrierende Felder**:
- `users.team` (String, nullable)
- `users.access_level` (Integer, default 1)
- Atualizar `users.role` para aceitar os novos valores
- `contracts.department` (String, nullable, indexed)
- `contracts.team` (String, nullable, indexed)
- `contracts.responsible_user_id` (Integer, nullable, indexed)

---

### 2. Atualizar Código Existente / Bestehenden Code aktualisieren

**DE**: Alle Referenzen auf die alten Rollen (USER, MANAGER, ADMIN) müssen aktualisiert werden.  
**PT**: Todas as referências aos papéis antigos (USER, MANAGER, ADMIN) devem ser atualizadas.

**Arquivos a verificar / Zu prüfende Dateien**:
- `backend/app/routers/*.py` (auth.py, users.py, contracts.py, etc.)
- `backend/app/services/*.py` (user_service.py, auth_service.py, etc.)
- `backend/test/*.py` (todos os testes)

**Buscar por / Suchen nach**:
```python
UserRole.USER → UserRole.STAFF
UserRole.MANAGER → UserRole.TEAM_LEAD ou DEPARTMENT_USER/ADM
UserRole.ADMIN → UserRole.SYSTEM_ADMIN ou DIRECTOR
```

---

### 3. Atualizar Testes / Tests aktualisieren

**DE**: Alle Unit- und Integrationstests müssen angepasst werden.  
**PT**: Todos os testes unitários e de integração devem ser ajustados.

**Exemplo / Beispiel**:
```python
# Antes / Vorher
user = User(role=UserRole.ADMIN)

# Depois / Nachher
user = User(
    role=UserRole.SYSTEM_ADMIN,
    access_level=AccessLevel.LEVEL_6,
    department="IT und Datenschutz"
)
```

---

### 4. Script de Migração de Dados / Datenmigrationsskript

Criar script para migrar usuários existentes:

```python
# backend/scripts/migrate_roles.py

from app.models.user import User, UserRole, AccessLevel

# Mapear roles antigos para novos
ROLE_MIGRATION_MAP = {
    "admin": {
        "role": UserRole.SYSTEM_ADMIN,
        "access_level": AccessLevel.LEVEL_6
    },
    "manager": {
        "role": UserRole.TEAM_LEAD,
        "access_level": AccessLevel.LEVEL_2
    },
    "user": {
        "role": UserRole.STAFF,
        "access_level": AccessLevel.LEVEL_1
    }
}

# Migrar usuários existentes
# ... (implementar lógica)
```

---

### 5. Atualizar Frontend / Frontend aktualisieren

**DE**: Wenn ein Frontend vorhanden ist, müssen die Rollen-Dropdowns und Berechtigungsprüfungen aktualisiert werden.  
**PT**: Se houver um frontend, os dropdowns de papéis e verificações de permissão devem ser atualizados.

---

### 6. Documentação de API / API-Dokumentation

**DE**: Swagger/OpenAPI-Dokumentation sollte die neuen Rollen und Felder reflektieren.  
**PT**: A documentação Swagger/OpenAPI deve refletir os novos papéis e campos.

---

##  Exemplos de Uso / Verwendungsbeispiele

### Exemplo 1: Verificar permissão de visualização

```python
from app.core.permissions import can_view_contract

def get_contract(contract_id: int, current_user: User, db: Session):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    if not can_view_contract(current_user, contract):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung / Sem permissão"
        )
    
    return contract
```

---

### Exemplo 2: Criar usuário com perfil padrão

```python
from app.core.permissions import PERFIS_PADRAO

def create_director_user(email: str, name: str, db: Session):
    perfil = PERFIS_PADRAO["Geschäftsführung"]
    
    user = User(
        email=email,
        name=name,
        role=perfil["role"],
        access_level=perfil["access_level"],
        department=perfil["department"],
        team=perfil["team"]
    )
    
    db.add(user)
    db.commit()
    return user
```

---

### Exemplo 3: Verificar múltiplas permissões

```python
from app.core.permissions import (
    can_edit_contract,
    can_delete_contract,
    can_approve_contract
)

def get_contract_permissions(user: User, contract: Contract):
    return {
        "can_view": can_view_contract(user, contract),
        "can_edit": can_edit_contract(user, contract),
        "can_delete": can_delete_contract(user, contract),
        "can_approve": can_approve_contract(user, contract)
    }
```

---

## ✅ Checklist de Implementação / Implementierungs-Checkliste

- [x]  Atualizar modelo User com novos roles e access_level
- [x]  Atualizar schemas Pydantic de User
- [x]  Adicionar campos department/team ao Contract
- [x]  Reescrever módulo permissions.py
- [x]  Criar dicionário PERFIS_PADRAO
- [ ]  Criar migração Alembic
- [ ]  Atualizar routers (auth.py, users.py, contracts.py)
- [ ]  Atualizar services (user_service.py, auth_service.py)
- [ ]  Criar script de migração de dados
- [ ]  Atualizar testes unitários
- [ ]  Atualizar testes de integração
- [ ]  Atualizar documentação de API (Swagger)
- [ ]  Testar sistema de permissões end-to-end

---

##  Contato / Kontakt

**DE**: Bei Fragen zur Implementierung wenden Sie sich an das Entwicklungsteam.  
**PT**: Em caso de dúvidas sobre a implementação, entre em contato com a equipe de desenvolvimento.

---

**Versão / Version**: 1.0  
**Última atualização / Letzte Aktualisierung**: 27.11.2025
