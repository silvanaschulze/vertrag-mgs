/**
 * Alert Badge Component
 * Komponente für Warnungsabzeichen
 * 
 * Badge com contador de alertas não lidos para exibir no menu
 * Badge mit Zähler für ungelesene Warnungen zur Anzeige im Menü
 */

import { useState, useEffect } from 'react';
import { Badge } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import alertsApi from '../../services/alertsApi';

/**
 * AlertBadge Component
 * 
 * Exibe ícone de notificações com badge de contador
 * Zeigt Benachrichtigungssymbol mit Zählerbadge
 * 
 * @param {Object} props
 * @param {number} props.refreshInterval - Intervalo de atualização em ms (padrão: 30000)
 * @param {boolean} props.showIcon - Se deve mostrar o ícone (padrão: true)
 */
const AlertBadge = ({ refreshInterval = 30000, showIcon = true }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  /**
   * Busca contagem de alertas não lidos
   * Anzahl ungelesener Warnungen abrufen
   */
  const fetchUnreadCount = async () => {
    try {
      const count = await alertsApi.getUnreadCount();
      console.log('📊 [AlertBadge] Alertas não lidos:', count);
      setUnreadCount(count);
    } catch (error) {
      console.error('❌ [AlertBadge] Erro ao buscar contagem:', error);
      // Em caso de erro, mantém o contador anterior
    } finally {
      setLoading(false);
    }
  };

  /**
   * Efeito inicial - busca contador
   * Anfangseffekt - Zähler abrufen
   */
  useEffect(() => {
    fetchUnreadCount();
  }, []);

  /**
   * Polling - atualiza contador periodicamente
   * Polling - Zähler regelmäßig aktualisieren
   */
  useEffect(() => {
    if (refreshInterval <= 0) return;

    const interval = setInterval(() => {
      fetchUnreadCount();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  /**
   * Se não deve mostrar ícone, retorna apenas o badge com o número
   * Wenn kein Symbol angezeigt werden soll, nur Badge mit Nummer zurückgeben
   */
  if (!showIcon) {
    return (
      <Badge
        badgeContent={unreadCount}
        color="error"
        max={99}
        invisible={loading || unreadCount === 0}
      />
    );
  }

  /**
   * Retorna ícone com badge
   * Symbol mit Badge zurückgeben
   */
  return (
    <Badge
      badgeContent={unreadCount}
      color="error"
      max={99}
      invisible={loading || unreadCount === 0}
    >
      <NotificationsIcon />
    </Badge>
  );
};

export default AlertBadge;
