import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalClose from "@mui/joy/ModalClose";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";
import Link from "@mui/material/Link";
import { useState } from "react";

const ContactButton = () => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <Button color="neutral" onClick={() => setOpen(true)} variant="outlined">
        Contact
      </Button>
      <Modal
        aria-labelledby="contact-title"
        aria-describedby="contact-desc"
        open={open}
        onClose={() => setOpen(false)}
        sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
      >
        <Sheet
          variant="outlined"
          sx={{
            maxWidth: 500,
            borderRadius: "md",
            p: 3,
            boxShadow: "lg",
          }}
        >
          <ModalClose variant="plain" sx={{ m: 1 }} />
          <Typography
            component="h2"
            id="contact-title"
            level="h4"
            textColor="inherit"
            fontWeight="lg"
            mb={1}
          >
            Contact
          </Typography>
          <Typography id="contact-desc" textColor="text.tertiary">
            If you'd like another label to be added or if you see something wrong and
            think I could help DM me on{" "}
            <Link href="https://instagram.com/ourcq.lofi" target="_blank">
              Instagram
            </Link>{" "}
            or at ourcq.music@gmail.com :)
          </Typography>
        </Sheet>
      </Modal>
    </>
  );
};

export default ContactButton;
