import React from 'react';
import './Video.css';


class Video extends React.Component {

    render() {
        return (
            <a className="Video" style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0.75), rgba(255,255,255,0.75)), url(' + this.props.dataFromParent.img + ')' }}
                 data-url={this.props.dataFromParent.url}
                 href={this.props.dataFromParent.url}
                 target="_blank"
            >
                <div className="video-name">{this.props.dataFromParent.name}</div>
            </a>
        );
    }
}

export default Video;
