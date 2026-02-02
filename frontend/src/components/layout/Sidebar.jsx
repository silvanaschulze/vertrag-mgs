/**
 * Sidebar - Barra Lateral de Navegação / Seitliche Navigationsleiste
 * 
 * Menu fixo à esquerda com filtro por role
 * Festes Menü links mit Rollenfilter
 */
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography, Divider } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Description as ContractsIcon,
  Upload as ImportIcon,
  Warning as AlertsIcon,
  CheckCircle as ApprovalsIcon,
  People as UsersIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import AlertBadge from '../alerts/AlertBadge';

const DRAWER_WIDTH = 240;

// Menu items em Alemão / Menüpunkte auf Deutsch
const menuItems = [
  { 
    id: 'dashboard', 
    label: 'Übersicht', 
    labelEn: 'Overview',
    icon: DashboardIcon, 
    path: '/app/dashboard' 
  },
  { 
    id: 'contracts', 
    label: 'Verträge', 
    labelEn: 'Contracts',
    icon: ContractsIcon, 
    path: '/app/contracts' 
  },
  { 
    id: 'import', 
    label: 'Import', 
    labelEn: 'Import',
    icon: ImportIcon, 
    path: '/app/import', 
    permission: 'contracts:import' 
  },
  { 
    id: 'alerts', 
    label: 'Warnungen', 
    labelEn: 'Alerts',
    icon: AlertsIcon, 
    path: '/app/alerts' 
  },
  { 
    id: 'approvals', 
    label: 'Genehmigungen', 
    labelEn: 'Approvals',
    icon: ApprovalsIcon, 
    path: '/app/approvals', 
    permission: 'approvals:view' 
  },
  { 
    id: 'users', 
    label: 'Benutzer', 
    labelEn: 'Users',
    icon: UsersIcon, 
    path: '/app/users', 
    permission: 'users:view' 
  },
  { 
    id: 'system', 
    label: 'System', 
    labelEn: 'System',
    icon: SettingsIcon, 
    path: '/app/system', 
    permission: 'system:config' 
  },
];

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, canViewMenu, isAllowed } = useAuthStore();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      {/* Logo e Título / Logo und Titel */}
      <Toolbar sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        gap: 1,
        py: 2 
      }}>
        <Box
          component="img"
          src="/logo.jpg"
          alt="Christburg Logo"
          sx={{ 
            maxWidth: '120px', 
            height: 'auto',
            borderRadius: 1
          }}
        />
        <Typography variant="h6" component="div" fontWeight={700} color="primary">
          Vertrag-MGS
        </Typography>
      </Toolbar>

      <Divider />

      {/* Informações do Usuário / Benutzerinformationen */}
      {user && (
        <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
          <Typography variant="body2" fontWeight={600} noWrap>
            {user.name}
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            {user.role}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Level: {user.access_level}
          </Typography>
        </Box>
      )}

      <Divider />

      {/* Menu de Navegação / Navigationsmenü */}
      <List sx={{ pt: 1 }}>
        {menuItems.map((item) => {
          // Verifica se pode ver no menu / Prüft Menüsichtbarkeit
          if (!canViewMenu(item.id)) return null;

          // Verifica permissão específica / Prüft spezifische Berechtigung
          if (item.permission && !isAllowed(item.permission)) return null;

          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <ListItem key={item.id} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.light',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.main',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon>
                  {/* Se for o item de alertas, mostra badge com contador */}
                  {item.id === 'alerts' ? (
                    <AlertBadge showIcon={true} />
                  ) : (
                    <Icon color={isActive ? 'inherit' : 'action'} />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={item.label}
                  secondary={item.labelEn}
                  secondaryTypographyProps={{
                    variant: 'caption',
                    sx: { fontSize: '0.7rem' }
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* Rodapé / Fußzeile */}
      <Box sx={{ mt: 'auto', p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          © 2026 Christburg
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
