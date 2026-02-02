export const USER_ROLES = {
  SYSTEM_ADMIN: 'SYSTEM_ADMIN',
  DIRECTOR: 'DIRECTOR',
  DEPARTMENT_ADM: 'DEPARTMENT_ADM',
  DEPARTMENT_USER: 'DEPARTMENT_USER',
  TEAM_LEAD: 'TEAM_LEAD',
  STAFF: 'STAFF',
  READ_ONLY: 'READ_ONLY',
};

export const USER_ROLE_LABELS = {
  SYSTEM_ADMIN: 'Systemadministrator / System Admin',
  DIRECTOR: 'Direktor / Director',
  DEPARTMENT_ADM: 'Abteilungsleiter / Department Admin',
  DEPARTMENT_USER: 'Abteilungsbenutzer / Department User',
  TEAM_LEAD: 'Teamleiter / Team Lead',
  STAFF: 'Mitarbeiter / Staff',
  READ_ONLY: 'Nur Lesen / Read Only',
};

export const ACCESS_LEVELS = {
  SYSTEM: 6,
  COMPANY: 5,
  DEPARTMENT: 4,
  DEPARTMENT_RESTRICTED: 3,
  TEAM: 2,
  OWN: 1,
};

export const ACCESS_LEVEL_LABELS = {
  6: 'Level 6',
  5: 'Level 5',
  4: 'Level 4',
  3: 'Level 3',
  2: 'Level 2',
  1: 'Level 1',
  0: 'Level 0',
};
/**
 * Constantes da Aplicação
 * Anwendungskonstanten
 * 
 * Define valores fixos usados em toda aplicação
 * Definiert feste Werte, die in der gesamten Anwendung verwendet werden
 */

/**
 * Status de Contratos (deve corresponder ao backend ContractStatus enum)
 * Vertragsstatus (muss mit Backend ContractStatus enum übereinstimmen)
 */
export const CONTRACT_STATUS = {
  DRAFT: 'DRAFT',                      // Draft / Entwurf
  ACTIVE: 'ACTIVE',                    // Active / Aktiv
  EXPIRED: 'EXPIRED',                  // Expired / Abgelaufen
  TERMINATED: 'TERMINATED',            // Terminated / Beendet
  PENDING_APPROVAL: 'PENDING_APPROVAL' // Pending Approval / Wartet auf Genehmigung
};

/**
 * Labels de Status em Alemão (para exibição)
 * Status-Labels auf Deutsch (zur Anzeige)
 */
export const CONTRACT_STATUS_LABELS = {
  [CONTRACT_STATUS.DRAFT]: 'Entwurf',
  [CONTRACT_STATUS.ACTIVE]: 'Aktiv',
  [CONTRACT_STATUS.EXPIRED]: 'Abgelaufen',
  [CONTRACT_STATUS.TERMINATED]: 'Beendet',
  [CONTRACT_STATUS.PENDING_APPROVAL]: 'Wartet auf Genehmigung'
};

/**
 * Labels de Status em Inglês (para logs/debug)
 * Status-Labels auf Englisch (für Logs/Debug)
 */
export const CONTRACT_STATUS_LABELS_EN = {
  [CONTRACT_STATUS.DRAFT]: 'Draft',
  [CONTRACT_STATUS.ACTIVE]: 'Active',
  [CONTRACT_STATUS.EXPIRED]: 'Expired',
  [CONTRACT_STATUS.TERMINATED]: 'Terminated',
  [CONTRACT_STATUS.PENDING_APPROVAL]: 'Pending Approval'
};

/**
 * Cores para chips de status
 * Farben für Status-Chips
 */
export const CONTRACT_STATUS_COLORS = {
  [CONTRACT_STATUS.DRAFT]: 'default',
  [CONTRACT_STATUS.ACTIVE]: 'success',
  [CONTRACT_STATUS.EXPIRED]: 'warning',
  [CONTRACT_STATUS.TERMINATED]: 'error',
  [CONTRACT_STATUS.PENDING_APPROVAL]: 'info'
};

/**
 * Tipos de Contratos (deve corresponder ao backend ContractType enum)
 * Vertragstypen (muss mit Backend ContractType enum übereinstimmen)
 */
export const CONTRACT_TYPES = {
  SERVICE: 'SERVICE',                // Service / Dienstleistung
  PRODUCT: 'PRODUCT',                // Product / Produkt
  EMPLOYMENT: 'EMPLOYMENT',          // Employment / Beschäftigung
  LEASE: 'LEASE',                    // Lease / Miete (antiga: miete)
  RENTAL: 'RENTAL',                  // Rental / Vermietung
  PARTNERSHIP: 'PARTNERSHIP',        // Partnership / Partnerschaft
  OTHER: 'OTHER'                     // Other / Sonstiges
};

/**
 * Labels de Tipos em Alemão (para exibição)
 * Typ-Labels auf Deutsch (zur Anzeige)
 */
export const CONTRACT_TYPE_LABELS = {
  [CONTRACT_TYPES.SERVICE]: 'Dienstleistung',
  [CONTRACT_TYPES.PRODUCT]: 'Produkt',
  [CONTRACT_TYPES.EMPLOYMENT]: 'Beschäftigung',
  [CONTRACT_TYPES.LEASE]: 'Pacht',
  [CONTRACT_TYPES.RENTAL]: 'Miete',
  [CONTRACT_TYPES.PARTNERSHIP]: 'Partnerschaft',
  [CONTRACT_TYPES.OTHER]: 'Sonstiges'
};

/**
 * Labels de Tipos em Inglês (para logs/debug)
 * Typ-Labels auf Englisch (für Logs/Debug)
 */
export const CONTRACT_TYPE_LABELS_EN = {
  [CONTRACT_TYPES.SERVICE]: 'Service',
  [CONTRACT_TYPES.PRODUCT]: 'Product',
  [CONTRACT_TYPES.EMPLOYMENT]: 'Employment',
  [CONTRACT_TYPES.LEASE]: 'Lease',
  [CONTRACT_TYPES.RENTAL]: 'Rental',
  [CONTRACT_TYPES.PARTNERSHIP]: 'Partnership',
  [CONTRACT_TYPES.OTHER]: 'Other'
};

/**
 * Configuração de paginação
 * Paginierungskonfiguration
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 25,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100]
};

/**
 * Moeda padrão
 * Standardwährung
 */
export const DEFAULT_CURRENCY = 'EUR';

/**
 * Formato de data para exibição
 * Datumsformat für Anzeige
 */
export const DATE_FORMAT = 'dd.MM.yyyy'; // Formato alemão / Deutsches Format

/**
 * Formato de data para API (ISO)
 * Datumsformat für API (ISO)
 */
export const DATE_FORMAT_API = 'yyyy-MM-dd';

/**
 * Formas Jurídicas de Empresas (deve corresponder ao backend LegalForm enum)
 * Rechtsformen für Unternehmen (muss mit Backend LegalForm enum übereinstimmen)
 */
export const LEGAL_FORMS = {
  GMBH: 'gmbh',
  UG: 'ug',
  AG: 'ag',
  KG: 'kg',
  OHG: 'ohg',
  GBR: 'gbr',
  EK: 'ek',
  EV: 'ev',
  KGAA: 'kgaa',
  GMBH_CO_KG: 'gmbh_co_kg',
  PARTG: 'partg',
  STIFTUNG: 'stiftung',
  GENOSSENSCHAFT: 'genossenschaft',
  SE: 'se',
  OTHER: 'sonstiges'
};

/**
 * Labels de Formas Jurídicas em Alemão
 * Rechtsform-Labels auf Deutsch
 */
export const LEGAL_FORM_LABELS = {
  [LEGAL_FORMS.GMBH]: 'GmbH',
  [LEGAL_FORMS.UG]: 'UG (haftungsbeschränkt)',
  [LEGAL_FORMS.AG]: 'AG',
  [LEGAL_FORMS.KG]: 'KG',
  [LEGAL_FORMS.OHG]: 'OHG',
  [LEGAL_FORMS.GBR]: 'GbR',
  [LEGAL_FORMS.EK]: 'Einzelkaufmann',
  [LEGAL_FORMS.EV]: 'e.V.',
  [LEGAL_FORMS.KGAA]: 'KGaA',
  [LEGAL_FORMS.GMBH_CO_KG]: 'GmbH & Co. KG',
  [LEGAL_FORMS.PARTG]: 'PartG',
  [LEGAL_FORMS.STIFTUNG]: 'Stiftung',
  [LEGAL_FORMS.GENOSSENSCHAFT]: 'eG',
  [LEGAL_FORMS.SE]: 'SE',
  [LEGAL_FORMS.OTHER]: 'Sonstiges'
};

/**
 * Labels de Formas Jurídicas em Inglês
 * Rechtsform-Labels auf Englisch
 */
export const LEGAL_FORM_LABELS_EN = {
  [LEGAL_FORMS.GMBH]: 'Limited Liability Company',
  [LEGAL_FORMS.UG]: 'Entrepreneurial Company (Limited)',
  [LEGAL_FORMS.AG]: 'Stock Corporation',
  [LEGAL_FORMS.KG]: 'Limited Partnership',
  [LEGAL_FORMS.OHG]: 'General Partnership',
  [LEGAL_FORMS.GBR]: 'Civil Law Partnership',
  [LEGAL_FORMS.EK]: 'Sole Proprietor',
  [LEGAL_FORMS.EV]: 'Registered Association',
  [LEGAL_FORMS.KGAA]: 'Partnership Limited by Shares',
  [LEGAL_FORMS.GMBH_CO_KG]: 'GmbH & Co. KG',
  [LEGAL_FORMS.PARTG]: 'Partnership Company',
  [LEGAL_FORMS.STIFTUNG]: 'Foundation',
  [LEGAL_FORMS.GENOSSENSCHAFT]: 'Cooperative',
  [LEGAL_FORMS.SE]: 'European Company',
  [LEGAL_FORMS.OTHER]: 'Other'
};

/**
 * Frequências de Pagamento (deve corresponder ao backend PaymentFrequency enum)
 * Zahlungsfrequenz (muss mit Backend PaymentFrequency enum übereinstimmen)
 */
export const PAYMENT_FREQUENCY = {
  MONTHLY: 'monatlich',
  QUARTERLY: 'vierteljährlich',
  SEMI_ANNUAL: 'halbjährlich',
  ANNUAL: 'jährlich',
  CUSTOM_YEARS: 'alle_x_jahre',
  ONE_TIME: 'einmalig'
};

/**
 * Labels de Frequência de Pagamento em Alemão
 * Zahlungsfrequenz-Labels auf Deutsch
 */
export const PAYMENT_FREQUENCY_LABELS = {
  [PAYMENT_FREQUENCY.MONTHLY]: 'Monatlich',
  [PAYMENT_FREQUENCY.QUARTERLY]: 'Vierteljährlich',
  [PAYMENT_FREQUENCY.SEMI_ANNUAL]: 'Halbjährlich',
  [PAYMENT_FREQUENCY.ANNUAL]: 'Jährlich',
  [PAYMENT_FREQUENCY.CUSTOM_YEARS]: 'Alle X Jahre',
  [PAYMENT_FREQUENCY.ONE_TIME]: 'Einmalig'
};

/**
 * Labels de Frequência de Pagamento em Inglês
 * Zahlungsfrequenz-Labels auf Englisch
 */
export const PAYMENT_FREQUENCY_LABELS_EN = {
  [PAYMENT_FREQUENCY.MONTHLY]: 'Monthly',
  [PAYMENT_FREQUENCY.QUARTERLY]: 'Quarterly',
  [PAYMENT_FREQUENCY.SEMI_ANNUAL]: 'Semi-Annual',
  [PAYMENT_FREQUENCY.ANNUAL]: 'Annual',
  [PAYMENT_FREQUENCY.CUSTOM_YEARS]: 'Every X Years',
  [PAYMENT_FREQUENCY.ONE_TIME]: 'One-Time'
};

/**
 * Departments / Bereiche
 * Departamentos / Setores (baseado em PERFIS_PADRAO do backend)
 */
export const DEPARTMENTS = [
  'Geschäftsführung',
  'Personal Organization und Finanzen',
  'Technischer Bereich',
  'IT und Datenschutz'
];

/**
 * Teams por Department / Teams nach Bereich
 * Times por Departamento (baseado em PERFIS_PADRAO do backend)
 */
export const TEAMS_BY_DEPARTMENT = {
  'Personal Organization und Finanzen': [
    'Finanzen und Rechnungswesen'
  ],
  'IT und Datenschutz': [
    'Informationstechnologie',
    'PR'
  ],
  'Technischer Bereich': [],
  'Geschäftsführung': []
};

/**
 * Todos os teams disponíveis / Alle verfügbaren Teams
 * Todos os times disponíveis
 */
export const ALL_TEAMS = [
  'Informationstechnologie',
  'PR',
  'Finanzen und Rechnungswesen'
];

/**
 * ========================================
 * ALERTAS / WARNUNGEN
 * ========================================
 */

/**
 * Tipos de Alertas (deve corresponder ao backend Alert.alert_type)
 * Warnungstypen (muss mit Backend Alert.alert_type übereinstimmen)
 */
export const ALERT_TYPES = {
  T_60: 'T-60',      // 60 dias antes do vencimento / 60 Tage vor Ablauf
  T_30: 'T-30',      // 30 dias antes / 30 Tage vor Ablauf
  T_10: 'T-10',      // 10 dias antes / 10 Tage vor Ablauf
  T_1: 'T-1',        // 1 dia antes / 1 Tag vor Ablauf
  CUSTOM: 'BENUTZERDEFINIERT'   // Alerta manual / Manuelle Warnung
};

/**
 * Labels de Tipos de Alertas (bilíngue Alemão/Inglês)
 * Warnungstyp-Labels (zweisprachig Deutsch/Englisch)
 */
export const ALERT_TYPE_LABELS = {
  'T-60': '60 Tage / 60 Days',
  'T-30': '30 Tage / 30 Days',
  'T-10': '10 Tage / 10 Days',
  'T-1': '1 Tag / 1 Day',
  'BENUTZERDEFINIERT': 'Benutzerdefiniert / Custom'
};

/**
 * Cores para chips de tipos de alertas
 * Farben für Warnungstyp-Chips
 */
export const ALERT_TYPE_COLORS = {
  'T-60': 'info',      // Azul - ainda distante / Blau - noch weit weg
  'T-30': 'warning',   // Laranja - atenção / Orange - Achtung
  'T-10': 'error',     // Vermelho - urgente / Rot - dringend
  'T-1': 'error',      // Vermelho - muito urgente / Rot - sehr dringend
  'BENUTZERDEFINIERT': 'default'  // Cinza - personalizado / Grau - benutzerdefiniert
};

/**
 * Status de Alertas (backend usa pending/sent/failed)
 * Warnungsstatus (Backend verwendet pending/sent/failed)
 */
export const ALERT_STATUS = {
  ALL: 'all',           // Todos / Alle
  PENDING: 'pending',   // Pendente / Ausstehend
  SENT: 'sent',         // Enviado / Gesendet
  FAILED: 'failed'      // Falhou / Fehlgeschlagen
};

/**
 * Labels de Status de Alertas
 * Warnungsstatus-Labels
 */
export const ALERT_STATUS_LABELS = {
  [ALERT_STATUS.ALL]: 'Alle / All',
  [ALERT_STATUS.PENDING]: 'Ausstehend / Pending',
  [ALERT_STATUS.SENT]: 'Gesendet / Sent',
  [ALERT_STATUS.FAILED]: 'Fehlgeschlagen / Failed'
};

/**
 * Cores para status de alertas
 * Farben für Warnungsstatus
 */
export const ALERT_STATUS_COLORS = {
  [ALERT_STATUS.PENDING]: 'warning',
  [ALERT_STATUS.SENT]: 'success',
  [ALERT_STATUS.FAILED]: 'error'
};

/**
 * ========================================
 * RENT STEPS / MIETSTAFFELUNGEN
 * ========================================
 */

/**
 * Moedas suportadas para Rent Steps
 * Unterstützte Währungen für Mietstaffelungen
 */
export const CURRENCIES = {
  EUR: 'EUR',
  USD: 'USD',
  GBP: 'GBP',
  CHF: 'CHF',
  BRL: 'BRL'
};

/**
 * Labels de moedas com símbolos
 * Währungs-Labels mit Symbolen
 */
export const CURRENCY_LABELS = {
  [CURRENCIES.EUR]: 'EUR (€)',
  [CURRENCIES.USD]: 'USD ($)',
  [CURRENCIES.GBP]: 'GBP (£)',
  [CURRENCIES.CHF]: 'CHF (Fr)',
  [CURRENCIES.BRL]: 'BRL (R$)'
};

/**
 * Símbolos de moedas
 * Währungssymbole
 */
export const CURRENCY_SYMBOLS = {
  [CURRENCIES.EUR]: '€',
  [CURRENCIES.USD]: '$',
  [CURRENCIES.GBP]: '£',
  [CURRENCIES.CHF]: 'Fr',
  [CURRENCIES.BRL]: 'R$'
};

/**
 * ========================================
 * APPROVALS / GENEHMIGUNGEN
 * ========================================
 */

/**
 * Status de Aprovações (deve corresponder ao backend ApprovalStatus enum)
 * Genehmigungsstatus (muss mit Backend ApprovalStatus enum übereinstimmen)
 */
export const APPROVAL_STATUS = {
  PENDING: 'pending',       // Aguardando / Ausstehend
  APPROVED: 'approved',     // Aprovado / Genehmigt
  REJECTED: 'rejected',     // Rejeitado / Abgelehnt
  CANCELLED: 'cancelled'    // Cancelado / Abgebrochen
};

/**
 * Labels de Status de Aprovações
 * Genehmigungsstatus-Labels
 */
export const APPROVAL_STATUS_LABELS = {
  [APPROVAL_STATUS.PENDING]: 'Ausstehend / Pendente',
  [APPROVAL_STATUS.APPROVED]: 'Genehmigt / Aprovado',
  [APPROVAL_STATUS.REJECTED]: 'Abgelehnt / Rejeitado',
  [APPROVAL_STATUS.CANCELLED]: 'Abgebrochen / Cancelado'
};

/**
 * Cores para status de aprovações
 * Farben für Genehmigungsstatus
 */
export const APPROVAL_STATUS_COLORS = {
  [APPROVAL_STATUS.PENDING]: 'warning',
  [APPROVAL_STATUS.APPROVED]: 'success',
  [APPROVAL_STATUS.REJECTED]: 'error',
  [APPROVAL_STATUS.CANCELLED]: 'default'
};
