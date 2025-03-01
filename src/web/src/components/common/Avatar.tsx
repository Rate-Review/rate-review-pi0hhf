import React from 'react'; // React library for building the component ^18.0.0
import styled from 'styled-components'; // CSS-in-JS library for component styling ^5.3.5

// Constants for avatar sizes with corresponding dimensions
const AVATAR_SIZES = {
  xs: '24px',
  sm: '32px',
  md: '40px',
  lg: '48px',
  xl: '64px'
};

// Constants for avatar font sizes corresponding to avatar sizes
const AVATAR_FONT_SIZES = {
  xs: '10px',
  sm: '12px',
  md: '14px',
  lg: '16px',
  xl: '20px'
};

// Array of colors for avatars
const AVATAR_COLORS = [
  '#2C5282', // deep blue (primary)
  '#38A169', // green (secondary)
  '#DD6B20', // orange (accent)
  '#3182CE', // blue (info)
  '#E53E3E', // red (error)
  '#805AD5', // purple
  '#D69E2E'  // yellow
];

// Type definition for the component props
interface AvatarProps {
  /** User's name used for initials and for color generation */
  name?: string;
  /** URL to the user's profile image */
  imageUrl?: string;
  /** Size of the avatar - xs, sm, md, lg, xl */
  size?: keyof typeof AVATAR_SIZES;
  /** Custom background color. If not provided, a color will be generated from the name */
  bgColor?: string;
  /** Whether to show a border around the avatar */
  showBorder?: boolean;
  /** Border color - defaults to white */
  borderColor?: string;
  /** Optional CSS class name */
  className?: string;
  /** Optional click handler */
  onClick?: () => void;
}

// Styled container for the avatar
const AvatarContainer = styled.div<{
  size: string;
  bgColor: string;
  showBorder: boolean;
  borderColor: string;
}>`
  width: ${props => props.size};
  height: ${props => props.size};
  border-radius: 50%;
  background-color: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  ${props => props.showBorder && `
    border: 2px solid ${props.borderColor};
    box-sizing: content-box;
  `}
  cursor: ${props => props.onClick ? 'pointer' : 'default'};
`;

// Styled image for the avatar
const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

// Styled text for the avatar initials
const AvatarInitials = styled.span<{ fontSize: string }>`
  color: white;
  font-size: ${props => props.fontSize};
  font-weight: 500;
  text-transform: uppercase;
  line-height: 1;
  user-select: none;
`;

/**
 * Extracts initials from a name string
 * @param name The full name to extract initials from
 * @returns A string containing the initials (maximum 2 characters)
 */
const getInitials = (name?: string): string => {
  if (!name) return '?';
  
  const nameParts = name.trim().split(/\s+/);
  
  if (nameParts.length === 0) return '?';
  
  if (nameParts.length === 1) {
    return nameParts[0].charAt(0).toUpperCase();
  }
  
  const firstInitial = nameParts[0].charAt(0);
  const lastInitial = nameParts[nameParts.length - 1].charAt(0);
  
  return (firstInitial + lastInitial).toUpperCase();
};

/**
 * Generates a deterministic color based on the user's name
 * @param name The name to generate a color from
 * @returns A color hex code from the AVATAR_COLORS array
 */
const getAvatarColor = (name?: string): string => {
  if (!name) return AVATAR_COLORS[0];
  
  // Simple hash function to get a consistent color for the same name
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Use the hash to get an index from the color array
  const index = Math.abs(hash) % AVATAR_COLORS.length;
  return AVATAR_COLORS[index];
};

/**
 * Avatar component that displays either a user's profile image or their initials
 * in a styled circle with configurable size, color, and border options.
 */
const Avatar: React.FC<AvatarProps> = ({
  name = '',
  imageUrl,
  size = 'md',
  bgColor,
  showBorder = false,
  borderColor = 'white',
  className,
  onClick,
  ...rest
}) => {
  // Determine the background color - use provided color or generate from name
  const backgroundColor = bgColor || getAvatarColor(name);
  
  // Get the appropriate size and font size based on the size prop
  const avatarSize = AVATAR_SIZES[size];
  const fontSize = AVATAR_FONT_SIZES[size];

  return (
    <AvatarContainer
      size={avatarSize}
      bgColor={backgroundColor}
      showBorder={showBorder}
      borderColor={borderColor}
      className={className}
      onClick={onClick}
      {...rest}
    >
      {imageUrl ? (
        <AvatarImage src={imageUrl} alt={name || 'User avatar'} />
      ) : (
        <AvatarInitials fontSize={fontSize}>
          {getInitials(name)}
        </AvatarInitials>
      )}
    </AvatarContainer>
  );
};

export default Avatar;