import React from 'react';
import PropTypes from 'prop-types';
import { DataGrid } from '@mui/x-data-grid';
import { Chip, Switch, IconButton, Tooltip } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import LockResetIcon from '@mui/icons-material/LockReset';
import DeleteIcon from '@mui/icons-material/Delete';
import { USER_ROLE_LABELS, ACCESS_LEVEL_LABELS } from '../../utils/constants';

const UserTable = ({
  users, loading, page, pageSize, totalRows,
  onPageChange, onPageSizeChange, onSortChange,
  onEdit, onResetPassword, onToggleActive, onDelete
}) => {
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Name', flex: 1 },
    { field: 'email', headerName: 'E-Mail', flex: 1.2 },
    {
      field: 'role',
      headerName: 'Role',
      width: 170,
      renderCell: (params) => (
        <Chip label={USER_ROLE_LABELS[params.value] || params.value} color="primary" size="small" />
      ),
    },
    {
      field: 'access_level',
      headerName: 'Access Level',
      width: 130,
      renderCell: (params) => ACCESS_LEVEL_LABELS[params.value] || params.value,
    },
    { field: 'department', headerName: 'Department', width: 140 },
    { field: 'team', headerName: 'Team', width: 120 },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 110,
      renderCell: (params) => (
        <Switch
          checked={params.value}
          color={params.value ? 'success' : 'default'}
          onChange={() => onToggleActive(params.row.id, !params.value)}
          inputProps={{ 'aria-label': 'toggle active' }}
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Aktionen',
      width: 180,
      sortable: false,
      renderCell: (params) => (
        <>
          <Tooltip title="Editieren / Edit">
            <IconButton onClick={() => onEdit(params.row.id)} size="small"><EditIcon /></IconButton>
          </Tooltip>
          <Tooltip title="Passwort zurücksetzen / Reset Password">
            <IconButton onClick={() => onResetPassword(params.row.id)} size="small"><LockResetIcon /></IconButton>
          </Tooltip>
          <Tooltip title="Löschen / Delete">
            <IconButton onClick={() => onDelete(params.row.id)} size="small" color="error"><DeleteIcon /></IconButton>
          </Tooltip>
        </>
      ),
    },
  ];

  return (
    <div style={{ height: 520, width: '100%' }}>
      <DataGrid
        rows={users}
        columns={columns}
        loading={loading}
        page={page}
        pageSize={pageSize}
        rowCount={totalRows}
        pagination
        paginationMode="server"
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
        sortingMode="server"
        onSortModelChange={(model) => onSortChange(model[0])}
        getRowClassName={(params) => !params.row.is_active ? 'user-inactive' : ''}
        disableSelectionOnClick
        autoHeight
      />
    </div>
  );
};

UserTable.propTypes = {
  users: PropTypes.array.isRequired,
  loading: PropTypes.bool,
  page: PropTypes.number,
  pageSize: PropTypes.number,
  totalRows: PropTypes.number,
  onPageChange: PropTypes.func,
  onPageSizeChange: PropTypes.func,
  onSortChange: PropTypes.func,
  onEdit: PropTypes.func,
  onResetPassword: PropTypes.func,
  onToggleActive: PropTypes.func,
  onDelete: PropTypes.func,
};

export default UserTable;
