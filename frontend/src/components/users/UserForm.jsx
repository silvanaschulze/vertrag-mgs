import React, { useEffect, useState } from 'react';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
// Campo de senha com ícone de olho
function PasswordField(props) {
  const { value, onChange, ...rest } = props;
  const [show, setShow] = useState(false);
  return (
    <TextField
      {...rest}
      type={show ? 'text' : 'password'}
      value={value}
      onChange={onChange}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <IconButton
              aria-label="toggle password visibility"
              onClick={() => setShow(s => !s)}
              edge="end"
            >
              {show ? <VisibilityOff /> : <Visibility />}
            </IconButton>
          </InputAdornment>
        )
      }}
    />
  );
}
import PropTypes from 'prop-types';
import { Box, TextField, Button, MenuItem, Checkbox, FormControlLabel, Grid } from '@mui/material';
import { USER_ROLES, USER_ROLE_LABELS, ACCESS_LEVELS, ACCESS_LEVEL_LABELS, DEPARTMENTS, TEAMS_BY_DEPARTMENT } from '../../utils/constants';

const UserForm = ({ initialData, onSubmit, onCancel, loading }) => {
  // Função para mapear role para access_level
  const getAccessLevelByRole = (role) => {
    switch (role) {
      case 'SYSTEM_ADMIN': return 6;
      case 'DIRECTOR': return 5;
      case 'DEPARTMENT_ADM': return 4;
      case 'DEPARTMENT_USER': return 3;
      case 'TEAM_LEAD': return 2;
      case 'STAFF': return 1;
      case 'READ_ONLY': return 1;
      default: return 1;
    }
  };
  const [form, setForm] = useState({
    username: '',
    name: '',
    email: '',
    password: '',
    role: 'STAFF',
    access_level: getAccessLevelByRole('STAFF'),
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
    if (name === 'role') {
      setForm(f => ({
        ...f,
        role: value,
        access_level: getAccessLevelByRole(value)
      }));
    } else {
      setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
    }
  };

  const validate = () => {
    const errs = {};
    if (!form.username) errs.username = 'Benutzername erforderlich / Username required';
    if (!form.name) errs.name = 'Name erforderlich / Required';
    if (!form.email) errs.email = 'E-Mail erforderlich / Required';
    else if (!/^[^@]+@[^@]+\.[^@]+$/.test(form.email)) errs.email = 'Ungültige E-Mail / Invalid email';
    if (!initialData && !form.password) errs.password = 'Passwort erforderlich / Required';
    if (form.password && form.password.length < 8) errs.password = 'Mindestens 8 Zeichen / At least 8 chars';
    if (form.password && !/[A-Z]/.test(form.password)) errs.password = 'Mindestens ein Großbuchstabe / Pelo menos uma letra maiúscula';
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
        {/* Campo de senha com ícone de olho para visualizar */}
        {!initialData && (
          <Grid item xs={12} sm={6}>
            <PasswordField
              label="Passwort / Password"
              name="password"
              value={form.password}
              onChange={handleChange}
              error={!!errors.password}
              helperText={errors.password || 'Mindestens 8 Zeichen, mindestens ein Großbuchstabe / Pelo menos 8 caracteres, pelo menos uma letra maiúscula'}
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
        {/* Access Level apenas leitura, calculado pelo Role */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Access Level"
            name="access_level"
            value={form.access_level}
            InputProps={{ readOnly: true }}
            fullWidth
          />
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
