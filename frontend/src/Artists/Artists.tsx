import Box from "@mui/joy/Box";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Typography from "@mui/joy/Typography";
import React from "react";
import { useNavigate } from "react-router";
import { ArtistIndex, DefaultService } from "../api";
import textMatchesQuery from "../Labels/LabelsTable/textMatchesQuery";
import Page from "../Page";

export default function Artists() {
  const [artists, setArtists] = React.useState<ArtistIndex["artists"]>([]);
  const [filteredArtists, setFilteredArtists] = React.useState<ArtistIndex["artists"]>(
    []
  );

  const navigate = useNavigate();

  React.useEffect(() => {
    DefaultService.getArtists().then((index) => setArtists(index.artists));
  }, []);

  return (
    <Page
      onSearch={(query) =>
        setFilteredArtists(
          query.length > 1
            ? artists.filter((artist) => textMatchesQuery(artist.name, query))
            : []
        )
      }
      title="lofi artists"
    >
      <Grid
        container
        spacing={{ sm: 2, xs: 1 }}
        sx={{
          "& img.artist-image": {
            clipPath: "circle()",
            height: 50,
            objectFit: "contain",
            width: 50,
          },
        }}
      >
        {filteredArtists.length > 0 ? null : (
          <Box borderRadius={4} display="flex" justifyContent="center" width="100%">
            <Typography color="neutral" sx={{ padding: 4 }}>
              Use the search box to select an artist.
            </Typography>
          </Box>
        )}
        {filteredArtists.map((artist) => (
          <Grid md={4} lg={3} xs={12}>
            <Sheet
              sx={{
                borderRadius: 4,
                cursor: "pointer",
                p: 1,
                "&:hover": { bgcolor: (theme) => theme.palette.background.tooltip },
              }}
              onClick={() => {
                navigate(`/artists/${artist.id}`);
              }}
            >
              <Box alignItems="center" display="flex" gap={2}>
                <img
                  alt={`${artist.name}`}
                  className="artist-image"
                  src={artist.imageUrlS ?? "DefaultArtistImage"}
                />
                {artist.name}
              </Box>
            </Sheet>
          </Grid>
        ))}
      </Grid>
    </Page>
  );
}
