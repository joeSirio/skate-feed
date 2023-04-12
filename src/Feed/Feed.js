import React from 'react';
import './Feed.css';
import Video from "./Video/Video";
import axios from "axios";
import { Autocomplete, TextField } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
    palette: {
        mode: 'dark'
    }
});

class Feed extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            videos: [],
            filtered_videos: [],
            sources: [],
            sections: [],
            filtered_sections: [],
            selected_source: null,
            selected_section: null
        };

        this.onSourceChange = this.onSourceChange.bind(this);
        this.onSectionChange = this.onSectionChange.bind(this);
    }

    componentDidMount(){
        this.getAll(1);
    }

    getAll(id) {
        axios.get(`http://127.0.0.1:5000/feed`)
        .then((response) => {
            let videos = response.data.map(record => ({
                name: record["Title"],
                url: record["Url"],
                img: record["ImgSrc"],
                upload_date: record["UploadDate"],
                watched: record["Watched"],
                source: record["Source"],
                section: record["Section"]
            }))
            let sources = [...new Set(response.data.map(item => item["Source"]))];
            let sections = [...new Set(response.data.map(item => item["Section"]))];
            
            this.setState({
                videos: videos,
                filtered_videos: videos,
                sources: sources,
                sections: sections,
                filtered_sections: sections
            })
        })
    }

    filterVideos() {
        let filtered_videos = this.state.videos
        
        if(this.state.selected_section !== null)
            filtered_videos = filtered_videos.filter(dataitem => dataitem.section === this.state.selected_section);
        
        if(this.state.selected_source !== null){
            filtered_videos = filtered_videos.filter(dataitem => dataitem.source === this.state.selected_source);
        }

        this.setState({
            filtered_videos: filtered_videos
        })
    }

    onSourceChange(event, value) {
        let selected_section = this.state.selected_section;
        let filtered_sections;

        if(value === null){
            filtered_sections = this.state.sections
        }
        else{
            filtered_sections = this.state.sections.filter(f => f.indexOf(value) !== -1);
        }

        if(value !== null && selected_section !== null && selected_section.indexOf(value) === -1){
            selected_section = null
        }
        this.setState({
            selected_source: value,
            filtered_sections: filtered_sections,
            selected_section: selected_section
        },
        this.filterVideos)
    }

    onSectionChange(event, value){
        this.setState({
            selected_section: value
        },
        this.filterVideos)
    }

    render() {
        return (
            <div className="Feed">
                <div className="feed-filters">
                    <ThemeProvider theme={darkTheme}>
                        <Autocomplete
                            id="source-combo-box"
                            options={this.state.sources}
                            sx={{width:300}}
                            renderInput={(params) => <TextField {...params} label="Websites" />}
                            onChange={this.onSourceChange}
                        />
                        
                        <Autocomplete
                            id="section-combo-box"
                            options={this.state.filtered_sections}
                            value={this.state.selected_section}
                            sx={{width:300}}
                            renderInput={(params) => <TextField {...params} label="Sections" />}
                            onChange={this.onSectionChange}
                        />
                    </ThemeProvider>
                </div>
                <div className="feed-wrapper">
                    {this.state.filtered_videos.map((dataitem, i) => {
                        console.log('Video Mapped');
                        return (<Video key={dataitem.name} dataFromParent={dataitem} />)
                    })}
                </div>
            </div>
        );
    }
}

export default Feed;
