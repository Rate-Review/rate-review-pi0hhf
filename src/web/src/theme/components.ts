/**
 * Material UI component style overrides for the Justice Bid application
 * Ensures consistent styling and branding across all UI components
 * Following design principles: Modern & Professional, Accessibility (WCAG 2.1 AA), and Responsive Design
 */

import { Components, Theme } from '@mui/material/styles';
import colors from './colors';
import spacing from './spacing';
import shadows from './shadows';
import typography from './typography';
import { easing, transitions, createTransition } from './transitions';

const components: Components<Omit<Theme, 'components'>> = {
  MuiButton: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        borderRadius: spacing.sm,
        padding: `${spacing.sm}px ${spacing.md}px`,
        fontWeight: typography.fontWeight.medium,
        transition: createTransition('all', transitions.normal),
        '&:focus-visible': {
          outline: `2px solid ${colors.primary.light}`,
          outlineOffset: '2px',
        },
      },
      contained: {
        boxShadow: shadows[2],
        '&:hover': {
          boxShadow: shadows[4],
        },
      },
      containedPrimary: {
        backgroundColor: colors.primary.main,
        '&:hover': {
          backgroundColor: colors.primary.dark,
        },
      },
      containedSecondary: {
        backgroundColor: colors.secondary.main,
        '&:hover': {
          backgroundColor: colors.secondary.dark,
        },
      },
      outlined: {
        borderWidth: '1px',
        '&:hover': {
          borderWidth: '1px',
        },
      },
      outlinedPrimary: {
        borderColor: colors.primary.main,
        '&:hover': {
          borderColor: colors.primary.dark,
          backgroundColor: colors.alpha(colors.primary.main, 0.04),
        },
      },
      outlinedSecondary: {
        borderColor: colors.secondary.main,
        '&:hover': {
          borderColor: colors.secondary.dark,
          backgroundColor: colors.alpha(colors.secondary.main, 0.04),
        },
      },
      sizeSmall: {
        padding: `${spacing.xs}px ${spacing.sm}px`,
        fontSize: typography.fontSize.sm,
      },
      sizeLarge: {
        padding: `${spacing.md}px ${spacing.lg}px`,
        fontSize: typography.fontSize.lg,
      },
      disabled: {
        opacity: 0.7,
      },
    },
  },
  
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: spacing.sm,
          transition: createTransition('all', transitions.normal),
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.primary.main,
            borderWidth: '2px',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.alpha(colors.primary.main, 0.7),
          },
          '&.Mui-error .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.error.main,
          },
          '&.Mui-disabled .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.alpha(colors.text.disabled, 0.3),
          },
        },
        '& .MuiInputLabel-root': {
          color: colors.text.secondary,
          '&.Mui-focused': {
            color: colors.primary.main,
          },
          '&.Mui-error': {
            color: colors.error.main,
          },
          '&.Mui-disabled': {
            color: colors.text.disabled,
          },
        },
        '& .MuiInputBase-input': {
          padding: `${spacing.sm}px ${spacing.md}px`,
          '&::placeholder': {
            color: colors.alpha(colors.text.secondary, 0.5),
            opacity: 1,
          },
        },
        '& .MuiFormHelperText-root': {
          marginLeft: spacing.xs,
          fontSize: typography.fontSize.sm,
          '&.Mui-error': {
            color: colors.error.main,
          },
        },
      },
    },
  },
  
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: spacing.md,
        boxShadow: shadows[2],
        overflow: 'hidden',
        transition: createTransition('all', transitions.normal),
        '&:hover': {
          boxShadow: shadows[3],
        },
      },
    },
  },
  
  MuiTabs: {
    styleOverrides: {
      root: {
        minHeight: spacing.xl,
        borderBottom: `1px solid ${colors.divider}`,
      },
      indicator: {
        height: 3,
        borderRadius: `${spacing.xs}px ${spacing.xs}px 0 0`,
        backgroundColor: colors.primary.main,
      },
      scrollButtons: {
        color: colors.text.secondary,
        '&.Mui-disabled': {
          opacity: 0.3,
        },
      },
    },
  },
  
  MuiTable: {
    styleOverrides: {
      root: {
        borderCollapse: 'separate',
        borderSpacing: 0,
      },
    },
  },
  
  MuiDialog: {
    styleOverrides: {
      root: {
        '& .MuiBackdrop-root': {
          backgroundColor: colors.alpha('#000', 0.5),
        },
      },
      paper: {
        borderRadius: spacing.md,
        boxShadow: shadows[5],
        padding: spacing.md,
      },
    },
  },
  
  MuiAlert: {
    styleOverrides: {
      root: {
        borderRadius: spacing.sm,
        padding: `${spacing.sm}px ${spacing.md}px`,
        alignItems: 'center',
      },
      standardSuccess: {
        backgroundColor: colors.alpha(colors.success.main, 0.12),
        color: colors.success.dark,
      },
      standardError: {
        backgroundColor: colors.alpha(colors.error.main, 0.12),
        color: colors.error.dark,
      },
      standardWarning: {
        backgroundColor: colors.alpha(colors.warning.main, 0.12),
        color: colors.warning.dark,
      },
      standardInfo: {
        backgroundColor: colors.alpha(colors.info.main, 0.12),
        color: colors.info.dark,
      },
      icon: {
        opacity: 0.9,
      },
      message: {
        padding: '8px 0',
        fontSize: typography.fontSize.md,
      },
      action: {
        paddingTop: 0,
        marginRight: 0,
      },
    },
  },
  
  MuiCheckbox: {
    styleOverrides: {
      root: {
        color: colors.text.secondary,
        padding: spacing.xs,
        transition: createTransition('all', transitions.fast),
        '&.Mui-checked': {
          color: colors.primary.main,
        },
        '&:hover': {
          backgroundColor: colors.alpha(colors.primary.main, 0.04),
        },
        '&.Mui-disabled': {
          color: colors.text.disabled,
        },
        '&:focus-visible': {
          outline: `2px solid ${colors.primary.light}`,
          outlineOffset: '2px',
        },
      },
    },
  },
  
  MuiRadio: {
    styleOverrides: {
      root: {
        color: colors.text.secondary,
        padding: spacing.xs,
        transition: createTransition('all', transitions.fast),
        '&.Mui-checked': {
          color: colors.primary.main,
        },
        '&:hover': {
          backgroundColor: colors.alpha(colors.primary.main, 0.04),
        },
        '&.Mui-disabled': {
          color: colors.text.disabled,
        },
        '&:focus-visible': {
          outline: `2px solid ${colors.primary.light}`,
          outlineOffset: '2px',
        },
      },
    },
  },
  
  MuiSwitch: {
    styleOverrides: {
      root: {
        padding: spacing.xs,
        width: 42,
        height: 26,
        '&:focus-visible': {
          outline: `2px solid ${colors.primary.light}`,
          outlineOffset: '2px',
        },
      },
      switchBase: {
        padding: 3,
        '&.Mui-checked': {
          transform: 'translateX(16px)',
          color: colors.background.paper,
          '& + .MuiSwitch-track': {
            backgroundColor: colors.primary.main,
            opacity: 1,
            border: 'none',
          },
          '&.Mui-disabled + .MuiSwitch-track': {
            opacity: 0.5,
          },
        },
        '&.Mui-disabled': {
          color: colors.background.paper,
          '& + .MuiSwitch-track': {
            opacity: 0.3,
          },
        },
      },
      thumb: {
        boxShadow: 'none',
        width: 20,
        height: 20,
      },
      track: {
        borderRadius: 13,
        border: `1px solid ${colors.text.secondary}`,
        backgroundColor: colors.alpha(colors.text.secondary, 0.3),
        opacity: 1,
        transition: createTransition(['background-color', 'border'], transitions.normal),
      },
    },
  },
  
  MuiSelect: {
    styleOverrides: {
      root: {
        '&.MuiOutlinedInput-root': {
          borderRadius: spacing.sm,
          transition: createTransition('all', transitions.normal),
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.primary.main,
            borderWidth: '2px',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.alpha(colors.primary.main, 0.7),
          },
          '&.Mui-error .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.error.main,
          },
          '&.Mui-disabled .MuiOutlinedInput-notchedOutline': {
            borderColor: colors.alpha(colors.text.disabled, 0.3),
          },
        },
      },
      select: {
        padding: `${spacing.sm}px ${spacing.lg}px ${spacing.sm}px ${spacing.md}px`,
        '&:focus': {
          backgroundColor: 'transparent',
        },
      },
      icon: {
        color: colors.text.secondary,
        right: spacing.sm,
      },
    },
  },
  
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundImage: 'none',
        backgroundColor: colors.background.paper,
        transition: createTransition('box-shadow', transitions.normal),
      },
      rounded: {
        borderRadius: spacing.md,
      },
      elevation1: {
        boxShadow: shadows[1],
      },
      elevation2: {
        boxShadow: shadows[2],
      },
      elevation3: {
        boxShadow: shadows[3],
      },
      elevation4: {
        boxShadow: shadows[4],
      },
      elevation5: {
        boxShadow: shadows[5],
      },
    },
  },
  
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        height: 32,
        fontSize: typography.fontSize.sm,
        transition: createTransition('all', transitions.fast),
        '&.MuiChip-colorPrimary': {
          backgroundColor: colors.alpha(colors.primary.main, 0.12),
          color: colors.primary.dark,
        },
        '&.MuiChip-colorSecondary': {
          backgroundColor: colors.alpha(colors.secondary.main, 0.12),
          color: colors.secondary.dark,
        },
        '&.MuiChip-colorSuccess': {
          backgroundColor: colors.alpha(colors.success.main, 0.12),
          color: colors.success.dark,
        },
        '&.MuiChip-colorError': {
          backgroundColor: colors.alpha(colors.error.main, 0.12),
          color: colors.error.dark,
        },
        '&.MuiChip-colorWarning': {
          backgroundColor: colors.alpha(colors.warning.main, 0.12),
          color: colors.warning.dark,
        },
        '&.MuiChip-colorInfo': {
          backgroundColor: colors.alpha(colors.info.main, 0.12),
          color: colors.info.dark,
        },
      },
      label: {
        paddingLeft: spacing.sm,
        paddingRight: spacing.sm,
        fontWeight: typography.fontWeight.medium,
      },
      deleteIcon: {
        color: 'currentColor',
        opacity: 0.7,
        '&:hover': {
          opacity: 1,
          color: 'currentColor',
        },
      },
      outlined: {
        backgroundColor: 'transparent',
        '&.MuiChip-colorPrimary': {
          borderColor: colors.primary.main,
          color: colors.primary.main,
        },
        '&.MuiChip-colorSecondary': {
          borderColor: colors.secondary.main,
          color: colors.secondary.main,
        },
      },
    },
  },
  
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        backgroundColor: colors.alpha(colors.text.primary, 0.9),
        color: colors.background.paper,
        padding: `${spacing.xs}px ${spacing.sm}px`,
        fontSize: typography.fontSize.sm,
        borderRadius: spacing.xs,
        fontWeight: typography.fontWeight.regular,
        boxShadow: shadows[2],
        maxWidth: 300,
      },
      arrow: {
        color: colors.alpha(colors.text.primary, 0.9),
      },
    },
  },
  
  MuiBadge: {
    styleOverrides: {
      root: {
        '& .MuiBadge-badge': {
          fontWeight: typography.fontWeight.medium,
          fontSize: typography.fontSize.xs,
          minWidth: 20,
          height: 20,
          padding: `0 ${spacing.xs}px`,
        },
      },
      colorPrimary: {
        backgroundColor: colors.primary.main,
        color: colors.primary.contrastText,
      },
      colorSecondary: {
        backgroundColor: colors.secondary.main,
        color: colors.secondary.contrastText,
      },
      colorError: {
        backgroundColor: colors.error.main,
        color: colors.error.contrastText,
      },
    },
  },
  
  MuiAccordion: {
    styleOverrides: {
      root: {
        borderRadius: spacing.sm,
        overflow: 'hidden',
        boxShadow: 'none',
        '&:before': {
          display: 'none',
        },
        '&.Mui-expanded': {
          margin: 0,
          '&:first-of-type': {
            marginTop: 0,
          },
        },
        '&:not(:last-child)': {
          borderBottom: `1px solid ${colors.divider}`,
        },
      },
    },
  },
  
  MuiList: {
    styleOverrides: {
      root: {
        padding: `${spacing.xs}px 0`,
      },
    },
  },
  
  MuiDivider: {
    styleOverrides: {
      root: {
        borderColor: colors.divider,
      },
      middle: {
        marginLeft: spacing.md,
        marginRight: spacing.md,
      },
    },
  },
  
  MuiLink: {
    styleOverrides: {
      root: {
        color: colors.primary.main,
        fontWeight: typography.fontWeight.medium,
        textDecoration: 'none',
        transition: createTransition('color', transitions.fast),
        '&:hover': {
          color: colors.primary.dark,
          textDecoration: 'underline',
        },
        '&:focus-visible': {
          outline: `2px solid ${colors.primary.light}`,
          outlineOffset: '2px',
        },
      },
    },
  },
  
  MuiBreadcrumbs: {
    styleOverrides: {
      root: {
        fontSize: typography.fontSize.sm,
        color: colors.text.secondary,
      },
      separator: {
        fontSize: typography.fontSize.sm,
        color: colors.text.disabled,
      },
      li: {
        fontSize: typography.fontSize.sm,
      },
    },
  },
};

export default components;