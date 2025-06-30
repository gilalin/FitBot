import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1976d2',
          color: '#fff',
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: '#fff',
        },
      },
    },
    MuiListItemText: {
      styleOverrides: {
        primary: {
          color: '#fff',
        },
      },
    },
  },
});

export default theme; 