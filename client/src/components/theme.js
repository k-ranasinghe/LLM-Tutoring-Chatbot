// theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        mode: 'dark', // Use 'dark' for dark theme
        background: {
            default: '#212121', // Dark background
            paper: '#1e1e1e', // Paper background
        },
        text: {
            primary: '#b4b4b4', // Primary text color
            secondary: '#b0bec5', // Secondary text color
        },
    },
});

export default theme;
