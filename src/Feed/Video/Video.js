import React from 'react';
import './Video.css';


class Video extends React.Component {

    render() {
        return (
            <div className="Video" style={{ backgroundImage: 'url(' + this.props.dataFromParent.img + ')' }}
                 data-url={this.props.dataFromParent.url}
                 onClick= { () => this.props.redirect(this.props.dataFromParent.url)}
            >
                <div className="video-name">{this.props.dataFromParent.name}</div>
            </div>
        );
    }
}

export default Video;
