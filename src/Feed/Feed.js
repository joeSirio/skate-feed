import React from 'react';
import './Feed.css';
import Video from "./Video/Video";

var data = [
    {name: 'IAGO CARRASCO: BANGIN!', url: 'https://theberrics.com/iago-carrasco-bangin', img: 'https://i.ytimg.com/vi_webp/7O6JPKfVSCE/maxresdefault.webp'},
    {name: 'DOUBLE BANGIN! OMAR HASSAN & GUI KHURY AT RTMF BOWL', url: 'https://theberrics.com/double-bangin-omar-hassan-gui-khury', img: 'https://i.ytimg.com/vi_webp/GaOrt__U4So/maxresdefault.webp'},
    {name: 'FUNA NAKAYAMA: BANGIN!', url: 'https://theberrics.com/funa-nakayama-bangin', img: 'https://i.ytimg.com/vi/0BevZ2xlVUQ/hqdefault.jpg'}
];

class Feed extends React.Component {state = { data : data}
    redirect = (value) => {
        window.location.href=value;
    }
    render() {
        return (
            <div className="Feed">
                <h1 className="feed-header">Feed</h1>
                <div className="feed-wrapper">
                    {this.state.data.map((dataitem, i) => {
                        console.log('Video Mapped');
                        return (<Video dataFromParent={dataitem} redirect={this.redirect} />)
                    })}
                </div>
            </div>
        );
    }
}

//
// function Feed() {
//     return (
//         <div className="Feed">
//             <h1>Feed</h1>
//             {this.props.Video.map((vid, i) => {
//                 console.log('Video Mapped');
//                 return (<Video key={vid} />)
//             })}
//         </div>
//     );
// }

export default Feed;
