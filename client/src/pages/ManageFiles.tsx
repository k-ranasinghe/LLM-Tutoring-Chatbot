import React, { useState, useEffect } from "react";
import { Container, TextField, Typography, IconButton, Box, List, ListItem, ListItemText, } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import SideBar from "../components/SideBar.tsx";

const ManageFiles: React.FC = () => {
  const [files, setFiles] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Filtered files based on search query
  const filteredFiles = files.filter((file) =>
    file.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async (query: string = "") => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/get-files`
      );
      if (!response.ok) throw new Error("Failed to fetch files");
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error(error);
      alert("Error fetching files");
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this file?")) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/delete-file/${id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete the file");
      }

      alert("File deleted successfully");
      fetchFiles(); // Refresh the list of recent files
    } catch (error) {
      console.error("Error deleting file:", error);
      alert("Error deleting file");
    }
  };

  const handleEdit = (id: number) => {
    // Implement edit logic here
  };

  return (
    <Box sx={{ display: 'flex' }}>  {/* Flex container for sidebar and content */}
      <SideBar />
      <Box sx={{ flexGrow: 1, padding: 3 }}>
        <style>
          {`
              ::-webkit-scrollbar {
                width: 20px; /* Width of the scrollbar */
                background: transparent; /* Transparent background */
              }
              ::-webkit-scrollbar-thumb {
                background-color: rgba(90, 90, 90, 0.8); /* Lighter thumb color */
                border-left: 4px solid #212121;
                border-right: 4px solid #212121;
              }
              ::-webkit-scrollbar-thumb:hover {
                background: rgba(90, 90, 90, 1); /* Darker thumb on hover */
              }
            `}
        </style>
        <Container sx={{ marginTop: "10vh" }}>
          <Typography variant="h4" gutterBottom>
            Manage Files
          </Typography>
          <Box mb={3}>
            <TextField
              label="Search"
              variant="outlined"
              sx={{ marginBottom: "5vh", marginTop: "3vh" }}
              value={searchQuery}
              onChange={handleSearchChange}
              fullWidth
            />
            {/* <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          disabled={loading}
          style={{ marginTop: 10 }}
        >
          Search
        </Button> */}
            <List>
              {filteredFiles.map((file) => (
                <ListItem
                  key={file.id}
                  sx={{
                    border: "1px solid #ddd",
                    borderRadius: 1,
                    marginBottom: 1,
                  }}
                >
                  <ListItemText
                    primary={file.file_name}
                    secondary={`Uploaded on: ${file.uploaded_at.slice(0, 10)}`}
                  />
                  <div>
                    <IconButton color="primary" onClick={() => handleEdit(file.id)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDelete(file.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </div>
                </ListItem>
              ))}
            </List>
          </Box>
          {/* <Grid container spacing={2}>
        {files.map((file) => (
          <Grid item xs={12} key={file.id}>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              border={1}
              borderRadius={1}
              p={2}
              borderColor="grey.400"
            >
              <Typography>
                {file.file_name} ({file.file_type})
              </Typography>
              <div>
                <IconButton color="primary" onClick={() => handleEdit(file.id)}>
                  <EditIcon />
                </IconButton>
                <IconButton color="error" onClick={() => handleDelete(file.id)}>
                  <DeleteIcon />
                </IconButton>
              </div>
            </Box>
          </Grid>
        ))}
      </Grid> */}
        </Container>
      </Box>
    </Box>
  );
};

export default ManageFiles;
