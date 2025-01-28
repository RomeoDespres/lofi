import Menu from "@mui/icons-material/Menu";
import Drawer from "@mui/joy/Drawer";
import IconButton from "@mui/joy/IconButton";
import List from "@mui/joy/List";
import ListItemButton from "@mui/joy/ListItemButton";
import * as React from "react";
import { NavLink } from "react-router";
import useIsMobile from "../useIsMobile";

export default function MobileSidebar() {
  const [open, setOpen] = React.useState(false);
  const isMobile = useIsMobile();

  if (isMobile || true)
    return (
      <>
        <IconButton variant="outlined" color="neutral" onClick={() => setOpen(true)}>
          <Menu />
        </IconButton>
        <Drawer open={open} onClose={() => setOpen(false)} size="sm">
          {/* <Box
            sx={{
              display: "flex",
              alignItems: "center",
              position: "fixed",
              right: "0px",
              zIndex: 1000,
              gap: 0.5,
              ml: "auto",
              mt: 1,
              mr: 2,
            }}
          >
            <ModalClose id="close-icon" sx={{ position: "initial" }} />
          </Box> */}
          <List
            size="lg"
            component="nav"
            sx={{
              flex: "none",
              fontSize: "xl",
              // "& > div": { justifyContent: "center" },
            }}
          >
            <ListItemButton>
              <NavLink style={getNavLinkStyle} to="/labels">
                labels
              </NavLink>
            </ListItemButton>
            <ListItemButton>
              <NavLink style={getNavLinkStyle} to="/artists">
                artists
              </NavLink>
            </ListItemButton>
          </List>
        </Drawer>
      </>
    );

  return null;
}

const getNavLinkStyle = ({ isActive }: { isActive: boolean }) => ({
  color: "inherit",
  fontWeight: isActive ? "bold" : "normal",
  textDecoration: "none",
  minWidth: "100%",
});
