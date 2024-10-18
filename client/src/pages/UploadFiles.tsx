import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Grid,
  Button,
  Box,
  CircularProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  TextField,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";
import SideBar from "../components/SideBar.tsx";

const UploadFiles: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [subject, setSubject] = useState<string>(""); // State for subject
  const [recentFiles, setRecentFiles] = useState<any[]>([]);

  // State for search query
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Filtered files based on search query
  const filteredFiles = recentFiles.filter((file) =>
    file.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles([...files, ...Array.from(event.target.files)]);
    }
  };

  const handleFileUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file); // Append file directly
    });
    formData.append("subject", subject); // Append subject

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload-files",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("File upload failed");
      }

      const result = await response.json();
      console.log(result); // Handle the response data
      alert("Files uploaded successfully!");
      setFiles([]);
      setSubject(""); // Clear subject input
      fetchRecentFiles();
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("Error uploading files");
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    fetchRecentFiles();
  }, []);

  const fetchRecentFiles = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/get-files");
      if (!response.ok) {
        throw new Error("Failed to fetch recent files");
      }

      const data = await response.json();
      setRecentFiles(data.reverse()); // Show only 5 most recent files
    } catch (error) {
      console.error("Error fetching recent files:", error);
    }
  };

  const handleFileRemove = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleDelete = async (fileId: number) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/delete-file/${fileId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete the file");
      }

      alert("File deleted successfully");
      fetchRecentFiles(); // Refresh the list of recent files
    } catch (error) {
      console.error("Error deleting file:", error);
      alert("Error deleting file");
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex' }}>  {/* Flex container for sidebar and content */}
        <SideBar />
        <Box sx={{ flexGrow: 1, padding: 3 }}>  {/* Content area with padding */}
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
              Upload Files
            </Typography>
            {/* <Box mt={4} p={3} borderRadius="15px" bgcolor="#171717">
              <Typography variant="h5" gutterBottom>
                Supported File Formats
              </Typography>

              <Box mb={3}>
                <Typography variant="h6" color="primary" gutterBottom>
                  Audio Formats:
                </Typography>
                <Typography variant="body1" paragraph style={{ marginBottom: '0px' }}>
                  Our platform supports a wide range of audio formats, ensuring compatibility with most audio files. You can upload and play files in the following formats:
                </Typography>
                <Typography variant="body1" paragraph>
                  <Tooltip title='MPEG-4 Audio' arrow><strong style={{ marginRight: '20px' }}>.m4a</strong></Tooltip>
                  <Tooltip title='MPEG-1 Audio Layer III' arrow><strong style={{ marginRight: '20px' }}>.mp3</strong></Tooltip>
                  <Tooltip title='Waveform Audio File Format' arrow><strong style={{ marginRight: '20px' }}>.wav</strong></Tooltip>
                  <Tooltip title='Ogg Vorbis' arrow><strong style={{ marginRight: '20px' }}>.ogg</strong></Tooltip>
                  <Tooltip title='Opus Audio' arrow><strong style={{ marginRight: '20px' }}>.opus</strong></Tooltip>
                  <Tooltip title='Free Lossless Audio Codec' arrow><strong style={{ marginRight: '20px' }}>.flac</strong></Tooltip>
                  <Tooltip title='MPEG-4 Video' arrow><strong style={{ marginRight: '20px' }}>.mp4</strong></Tooltip>
                  <Tooltip title='WebM Audio (also include video)' arrow><strong style={{ marginRight: '20px' }}>.webm</strong></Tooltip>
                  <Tooltip title='MPEG Audio (also include video)' arrow><strong style={{ marginRight: '20px' }}>.mpeg</strong></Tooltip>
                </Typography>
              </Box>

              <Box mb={3}>
                <Typography variant="h6" color="secondary" gutterBottom>
                  Video Formats:
                </Typography>
                <Typography variant="body1" paragraph style={{ marginBottom: '0px' }}>
                  Our system also supports various video formats, providing flexibility for different types of video content. The following formats are supported:
                </Typography>
                <Typography variant="body1" paragraph>
                  <Tooltip title='MPEG-4 Video' arrow><strong style={{ marginRight: '20px' }}>.mp4</strong></Tooltip>
                  <Tooltip title='WebM Video' arrow><strong style={{ marginRight: '20px' }}>.webm</strong></Tooltip>
                  <Tooltip title='Audio Video Interleave' arrow><strong style={{ marginRight: '20px' }}>.avi</strong></Tooltip>
                  <Tooltip title='QuickTime Movie' arrow><strong style={{ marginRight: '20px' }}>.mov</strong></Tooltip>
                  <Tooltip title='Matroska Video' arrow><strong style={{ marginRight: '20px' }}>.mkv</strong></Tooltip>
                  <Tooltip title='MPEG Video' arrow><strong style={{ marginRight: '20px' }}>.mpeg</strong></Tooltip>
                  <Tooltip title='Ogg Theora' arrow><strong style={{ marginRight: '20px' }}>.ogg</strong></Tooltip>
                </Typography>
              </Box>

              <Box>
                <Typography variant="h6" color="textPrimary" gutterBottom>
                  Text Formats:
                </Typography>
                <Typography variant="body1" paragraph style={{ marginBottom: '0px' }}>
                  For document and text file uploads, we support the following formats, allowing for a broad range of document types and structures:
                </Typography>
                <Typography variant="body1" paragraph>
                  <Tooltip title='Portable Document Format' arrow><strong style={{ marginRight: '20px' }}>.pdf</strong></Tooltip>
                  <Tooltip title='Microsoft Word Document' arrow><strong style={{ marginRight: '20px' }}>.docx</strong></Tooltip>
                  <Tooltip title='Microsoft PowerPoint Presentation' arrow><strong style={{ marginRight: '20px' }}>.pptx</strong></Tooltip>
                  <Tooltip title='Plain Text File' arrow><strong style={{ marginRight: '20px' }}>.txt</strong></Tooltip>
                  <Tooltip title='Microsoft Excel Spreadsheet' arrow><strong style={{ marginRight: '20px' }}>.xlsx</strong></Tooltip>
                  <Tooltip title='Comma-Separated Values' arrow><strong style={{ marginRight: '20px' }}>.csv</strong></Tooltip>
                  <Tooltip title='Jupyter Notebook' arrow><strong style={{ marginRight: '20px' }}>.ipynb</strong></Tooltip>
                  <Tooltip title='Python Script' arrow><strong style={{ marginRight: '20px' }}>.py</strong></Tooltip>
                  <Tooltip title='HyperText Markup Language' arrow><strong style={{ marginRight: '20px' }}>.html</strong></Tooltip>
                  <Tooltip title='Markdown File' arrow><strong style={{ marginRight: '20px' }}>.md</strong></Tooltip>
                  <Tooltip title='Electronic Publication' arrow><strong style={{ marginRight: '20px' }}>.epub</strong></Tooltip>
                  <Tooltip title='Extensible Markup Language' arrow><strong style={{ marginRight: '20px' }}>.xml</strong></Tooltip>
                </Typography>
              </Box>
            </Box> */}
            <Grid container spacing={2} style={{ marginTop: '20px' }}>
              <Grid item xs={12}>
                <Button
                  variant="contained"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  fullWidth
                >
                  Select Files
                  <input type="file" hidden multiple onChange={handleFileChange} />
                </Button>
              </Grid>
            </Grid>
            <Box mt={2}>
              {files.length > 0 && (
                <Box mt={2}>
                  <Typography variant="h6">Selected Files</Typography>
                  <Grid container spacing={2}>
                    {files.map((file, index) => (
                      <Grid item xs={12} key={index}>
                        <Box
                          display="flex"
                          alignItems="center"
                          justifyContent="space-between"
                          border={1}
                          borderRadius={1}
                          p={2}
                          borderColor="grey.400"
                        >
                          <Typography>{file.name}</Typography>
                          <IconButton
                            color="error"
                            onClick={() => handleFileRemove(index)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </Box>
            <Box mt={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth variant="outlined" size="small">
                  <InputLabel>Subject</InputLabel>
                  <Select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value as string)}
                    label="Subject"
                    style={{ fontSize: '1.1rem' }}
                  >
                    <MenuItem value="">Select a subject</MenuItem>
                    <MenuItem value="Electronics">Electronics - I</MenuItem>
                    <MenuItem value="Electronics">Electronics - II</MenuItem>
                    <MenuItem value="Embedded Systems">Embedded Systems - I</MenuItem>
                    <MenuItem value="Embedded Systems">Embedded Systems - II</MenuItem>
                    <MenuItem value="Programming">Programming and Algorithms - I</MenuItem>
                    <MenuItem value="Programming">Programming and Algorithms - II</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Box>
            <Box mt={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleFileUpload}
                disabled={files.length === 0 || uploading || !subject}
                fullWidth
              >
                {uploading ? <CircularProgress size={24} /> : "Upload Files"}
              </Button>
            </Box>
          </Container>

          <Container>
            <Box mt={4}>
              <Typography variant="h6" gutterBottom>
                Uploaded Files
              </Typography>
              <TextField
                label="Search Files"
                variant="outlined"
                fullWidth
                margin="normal"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Box
                sx={{
                  maxHeight: 500, // Adjust height for scrollable area
                  overflowY: "auto", // Enable vertical scroll
                  border: "1px solid #ddd", // Optional: Add border for visual distinction
                  borderRadius: 1, // Optional: Add rounded corners
                  padding: 2, // Optional: Add padding inside the scrollable area
                }}
              >
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
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => handleDelete(file.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Box>
          </Container>
        </Box>
      </Box>
    </>
  );
};

export default UploadFiles;
