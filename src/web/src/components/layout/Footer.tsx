import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { Box, useTheme, Typography } from '@mui/material';
import { ROUTES } from '../../constants/routes';
import { useWindowSize } from '../../hooks/useWindowSize';

/**
 * Footer container component styled with a border and responsive layout
 */
const FooterContainer = styled(Box)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${({ theme }) => theme.spacing(2, 4)};
  border-top: 1px solid ${({ theme }) => theme.palette.divider};
  background-color: ${({ theme }) => theme.palette.background.paper};
  min-height: 60px;
  width: 100%;
  @media (max-width: 768px) {
    flex-direction: column;
    padding: ${({ theme }) => theme.spacing(2)};
  }
`;

/**
 * Container for footer links with responsive spacing
 */
const FooterLinks = styled(Box)`
  display: flex;
  gap: ${({ theme }) => theme.spacing(3)};
  @media (max-width: 768px) {
    margin-top: ${({ theme }) => theme.spacing(1)};
    gap: ${({ theme }) => theme.spacing(2)};
  }
`;

/**
 * Styled link component for footer navigation
 */
const FooterLink = styled(Link)`
  color: ${({ theme }) => theme.palette.text.secondary};
  text-decoration: none;
  font-size: 0.875rem;
  &:hover {
    color: ${({ theme }) => theme.palette.primary.main};
    text-decoration: underline;
  }
`;

/**
 * Copyright text component
 */
const Copyright = styled(Typography)`
  color: ${({ theme }) => theme.palette.text.secondary};
  font-size: 0.875rem;
`;

/**
 * Footer component that displays at the bottom of the application layout
 * Includes copyright information and links to important pages
 * 
 * @returns {JSX.Element} Rendered footer component
 */
const Footer: React.FC = () => {
  const theme = useTheme();
  const { width } = useWindowSize();
  const currentYear = new Date().getFullYear();

  // Define fallback routes in case they're not defined in ROUTES
  const termsRoute = (ROUTES as any).TERMS || '/terms';
  const privacyRoute = (ROUTES as any).PRIVACY || '/privacy';
  const helpRoute = (ROUTES as any).HELP || '/help';

  return (
    <FooterContainer>
      <Copyright>
        © {currentYear} Justice Bid. All rights reserved.
      </Copyright>
      <FooterLinks>
        <FooterLink to={termsRoute}>
          Terms of Service
        </FooterLink>
        <FooterLink to={privacyRoute}>
          Privacy Policy
        </FooterLink>
        <FooterLink to={helpRoute}>
          Help Center
        </FooterLink>
      </FooterLinks>
    </FooterContainer>
  );
};

export default Footer;