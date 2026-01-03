/**
 * Header - Barra Superior / Obere Leiste
 * 
 * Topbar com notificações, avatar e logout
 * Topbar mit Benachrichtigungen, Avatar und Logout
 */
import { AppBar, Toolbar, Typography, IconButton, Box, Menu, MenuItem, Badge, Avatar, Divider } from '@mui/material';
import { 
  Notifications as NotificationsIcon, 
  AccountCircle as AccountIcon,
  Logout as LogoutIcon 
} from '@mui/icons-material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const DRAWER_WIDTH = 240;

const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleMenuClose();
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        width: `calc(100% - ${DRAWER_WIDTH}px)`,
        ml: `${DRAWER_WIDTH}px`,
      }}
    >
      <Toolbar>
        {/* Título da Página / Seitentitel */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Vertragsverwaltungssystem / Contract Management System
        </Typography>

        {/* Notificações / Benachrichtigungen */}
        <IconButton color="inherit" sx={{ mr: 1 }}>
          <Badge badgeContent={0} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>

        {/* Avatar e Menu do Usuário / Avatar und Benutzermenü */}
        <IconButton
          color="inherit"
          onClick={handleMenuOpen}
          aria-label="user menu"
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.dark' }}>
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </Avatar>
        </IconButton>

        {/* Menu Dropdown / Dropdown-Menü */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          {/* Informações do Usuário / Benutzerinformationen */}
          <Box sx={{ px: 2, py: 1.5, minWidth: 200 }}>
            <Typography variant="subtitle1" fontWeight={600}>
              {user?.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.email}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              {user?.role} • Level {user?.access_level}
            </Typography>
          </Box>

          <Divider />

          {/* Opção de Perfil / Profiloption */}
          <MenuItem onClick={handleMenuClose}>
            <AccountIcon fontSize="small" sx={{ mr: 1.5 }} />
            Profil / Profile
          </MenuItem>

          <Divider />

          {/* Logout */}
          <MenuItem onClick={handleLogout}>
            <LogoutIcon fontSize="small" sx={{ mr: 1.5 }} />
            Abmelden / Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
