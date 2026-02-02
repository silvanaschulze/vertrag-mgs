import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Box, TextField, Button, MenuItem, Checkbox, FormControlLabel, Grid } from '@mui/material';
import { USER_ROLES, USER_ROLE_LABELS, ACCESS_LEVELS, ACCESS_LEVEL_LABELS, DEPARTMENTS, TEAMS_BY_DEPARTMENT } from '../../utils/constants';

const UserForm = ({ initialData, onSubmit, onCancel, loading }) => {
  const [form, setForm] = useState({
    username: '',
    name: '',
    email: '',
    password: '',
    role: 'STAFF',
    access_level: 1,
    department: '',
    team: '',
    is_active: true,
    ...initialData,
  });
  const [availableTeams, setAvailableTeams] = useState([]);

  // Atualiza teams disponíveis ao mudar departamento OU ao carregar dados iniciais
  useEffect(() => {
    if (form.department && TEAMS_BY_DEPARTMENT[form.department]) {
      setAvailableTeams(TEAMS_BY_DEPARTMENT[form.department]);
    } else {
      setAvailableTeams([]);
    }
    // Limpa o team se não existir no novo departamento
    if (form.team && (!form.department || !TEAMS_BY_DEPARTMENT[form.department]?.includes(form.team))) {
      setForm(f => ({ ...f, team: '' }));
    }
  }, [form.department, initialData]);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setForm(f => ({ ...f, ...initialData }));
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const validate = () => {
    const errs = {};
    if (!form.username) errs.username = 'Benutzername erforderlich / Username required';
    if (!form.name) errs.name = 'Name erforderlich / Required';
    if (!form.email) errs.email = 'E-Mail erforderlich / Required';
    else if (!/^[^@]+@[^@]+\.[^@]+$/.test(form.email)) errs.email = 'Ungültige E-Mail / Invalid email';
    if (!initialData && !form.password) errs.password = 'Passwort erforderlich / Required';
    if (form.password && form.password.length < 8) errs.password = 'Mindestens 8 Zeichen / At least 8 chars';
    if (!form.role) errs.role = 'Role erforderlich / Required';
    return errs;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      onSubmit(form);
    }
  };

  return (
    <form onSubmit={handleSubmit} autoComplete="off">
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Benutzername / Username"
            name="username"
            value={form.username}
            onChange={handleChange}
            error={!!errors.username}
            helperText={errors.username}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Name"
            name="name"
            value={form.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="E-Mail"
            name="email"
            value={form.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
            fullWidth
            required
          />
        </Grid>
        {!initialData && (
          <Grid item xs={12} sm={6}>
            <TextField
              label="Passwort / Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              error={!!errors.password}
              helperText={errors.password}
              fullWidth
              required
            />
          </Grid>
        )}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Role"
            name="role"
            value={form.role}
            onChange={handleChange}
            error={!!errors.role}
            helperText={errors.role}
            fullWidth
            required
          >
            {Object.keys(USER_ROLES).map(role => (
              <MenuItem key={role} value={role}>{USER_ROLE_LABELS[role]}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Abteilung / Department"
            name="department"
            value={form.department}
            onChange={handleChange}
            fullWidth
            required
          >
            <MenuItem value="">---</MenuItem>
            {DEPARTMENTS.map(dep => (
              <MenuItem key={dep} value={dep}>{dep}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Team"
            name="team"
            value={form.team}
            onChange={handleChange}
            fullWidth
            disabled={!form.department || availableTeams.length === 0}
          >
            <MenuItem value="">---</MenuItem>
            {availableTeams.map(team => (
              <MenuItem key={team} value={team}>{team}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            select
            label="Access Level"
            name="access_level"
            value={form.access_level}
            onChange={handleChange}
            fullWidth
            required
          >
            {Object.entries(ACCESS_LEVEL_LABELS).map(([level, label]) => (
              <MenuItem key={level} value={Number(level)}>{label}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControlLabel
            control={<Checkbox checked={form.is_active} onChange={handleChange} name="is_active" />}
            label="Aktiv / Active"
          />
        </Grid>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button type="submit" variant="contained" disabled={loading}>Speichern / Save</Button>
            <Button onClick={onCancel} variant="outlined" disabled={loading}>Abbrechen / Cancel</Button>
          </Box>
        </Grid>
      </Grid>
    </form>
  );
};

UserForm.propTypes = {
  initialData: PropTypes.object,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

export default UserForm;
