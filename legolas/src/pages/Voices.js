import React, { Component } from 'react';
import {
    View,
    Text,
    Platform,
    StyleSheet,
    TouchableHighlight,
    PermissionsAndroid,
    Dimensions,
    ActivityIndicator,
    Alert,
    KeyboardAvoidingView
} from "react-native";
import { GiftedChat } from 'react-native-gifted-chat';
import axios from 'axios';
import Sound from 'react-native-sound';
import NavigationBar from "react-native-navbar";
import { AudioRecorder, AudioUtils } from "react-native-audio";
import Ionicons from "react-native-vector-icons/Ionicons";

export default class Voices extends Component {
  constructor(props){
    super(props)
    this.dataPeople = null;
    this.state = {
      messages: [],
      currentTime: 0.0,
      recording: false,
      paused: false,
      stoppedRecording: false,
      finished: false,
      audioPath: `${
        AudioUtils.DocumentDirectoryPath
      }/${this.messageIdGenerator()}test.aac`,
      hasPermission: undefined,
    }
  }

  prepareRecordingPath(audioPath){
    AudioRecorder.prepareRecordingAtPath(audioPath, {
      SampleRate: 22050,
      Channels: 1,
      AudioQuality: "Low",
      AudioEncoding: "aac",
      AudioEncodingBitRate: 32000,
      IncludeBase64: true
    });
  }

  messageIdGenerator() {
    // generates uuid.
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
        let r = (Math.random() * 16) | 0,
            v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
  }

  _renderButton(title, onPress, active) {
    var style = (active) ? styles.activeButtonText : styles.buttonText;

    return (
      <TouchableHighlight style={styles.button} onPress={onPress}>
        <Text style={style}>
          {title}
        </Text>
      </TouchableHighlight>
    );
  }

  _renderPauseButton(onPress, active) {
    var style = (active) ? styles.activeButtonText : styles.buttonText;
    var title = this.state.paused ? "RESUME" : "PAUSE";
    return (
      <TouchableHighlight style={styles.button} onPress={onPress}>
        <Text style={style}>
          {title}
        </Text>
      </TouchableHighlight>
    );
  }

  async _pause() {
    if (!this.state.recording) {
      console.warn('Can\'t pause, not recording!');
      return;
    }

    try {
      const filePath = await AudioRecorder.pauseRecording();
      this.setState({paused: true});
    } catch (error) {
      console.error(error);
    }
  }

  async _resume() {
    if (!this.state.paused) {
      console.warn('Can\'t resume, not paused!');
      return;
    }

    try {
      await AudioRecorder.resumeRecording();
      this.setState({paused: false});
    } catch (error) {
      console.error(error);
    }
  }

  async _stop() {
    if (!this.state.recording) {
      console.warn('Can\'t stop, not recording!');
      return;
    }

    this.setState({stoppedRecording: true, recording: false, paused: false});

    try {
      const filePath = await AudioRecorder.stopRecording();

      if (Platform.OS === 'android') {
        this._finishRecording(true, filePath);
      }
      return filePath;
    } catch (error) {
      console.error(error);
    }
  }

  async _play() {
    if (this.state.recording) {
      await this._stop();
    }

    // These timeouts are a hacky workaround for some issues with react-native-sound.
    // See https://github.com/zmxv/react-native-sound/issues/89.
    setTimeout(() => {
      var sound = new Sound(this.state.audioPath, '', (error) => {
        if (error) {
          console.log('failed to load the sound', error);
        }
      });

      setTimeout(() => {
        sound.play((success) => {
          if (success) {
            console.log('successfully finished playing');
          } else {
            console.log('playback failed due to audio decoding errors');
          }
        });
      }, 100);
    }, 100);
  }

  async _record() {
    if (this.state.recording) {
      console.warn('Already recording!');
      return;
    }

    if (!this.state.hasPermission) {
      console.warn('Can\'t record, no permission granted!');
      return;
    }

    if(this.state.stoppedRecording){
      this.prepareRecordingPath(this.state.audioPath);
    }

    this.setState({recording: true, paused: false});

    try {
      const filePath = await AudioRecorder.startRecording();
    } catch (error) {
      console.error(error);
    }
  }

  _finishRecording(didSucceed, filePath, fileSize) {
    this.setState({ finished: didSucceed });
    console.log(`Finished recording of duration ${this.state.currentTime} seconds at path: ${filePath} and size of ${fileSize || 0} bytes`);
  }
  
  componentWillMount() {
    const { navigation } = this.props;
    this.nameCap = navigation.getParam('name', 'NO-ID');
    const speak = {
      name: this.nameCap,
      persist: false
    }
    axios.post('http://192.168.42.89:2931/chat/start_conversation', speak)
      .then(res => this.receivedName(res));
    
  }

  soundInitalConversation = function(messages){
    const speak = {
      name: this.nameCap,
      id: this.dataPeople.id,
      message: messages,
      persist: false,
      bot_audio: true
    }
    axios.post('http://192.168.42.89:2931/chat/send_message', speak)
      .then(res => this.playSound(res.data.speechs));
  }

  receivedName = function(res){
    this.dataPeople = res.data;
    //this.soundInitalConversation(res.data.messages);
    this.setState({
      messages: [
        {
          _id: 1,
          text: res.data.messages,
          createdAt: new Date(),
          user: {
            _id: 2,
            name: 'React Native',
            avatar: 'https://tsume-art.com/storage/app/uploads/public/82b/436/eac/thumb__1440x0_0_0_crop.jpg',
          },
        },
      ],
    })
  }

  onSend(messages = [], user=true) {
    this.setState(previousState => ({
      messages: GiftedChat.append(previousState.messages, messages),
    }));
    if(user){
      this.mensageBot(messages);
    }
  }

  playSound = function(base64P){
    const obj = {
      base64:base64P
    }
    axios.post('http://192.168.42.89:2931/chat/audio_gambira', obj)
      .then(res => this.soundLegolas(res.data))
    //this.soundLegolas('http://cafofobinladen.com.br/audio.mp3');
  }

  soundLegolas = function(audio){
    const sound = new Sound(audio, Sound.MAIN_BUNDLE, (error) => {
        if (error) {
          console.warn(error);
        }
        
        // play when loaded
        sound.play();
      });
  }

  mensageBot = function(messages = []){
    const speak = {
      name: this.nameCap,
      id: this.dataPeople.id,
      message: messages[0].text,
      persist: false
    }
    axios.post('http://192.168.42.89:2931/chat/send_message', speak)
      .then(res => this.onSend(this.bot(res.data.messages), false))
  }

  audioBot = function(audioBase64){
    const speak = {
      name: this.nameCap,
      id: this.dataPeople.id,
      audio: audioBase64,
      persist: false
    }
    
    axios.post('http://192.168.42.89:2931/chat/send_message', speak)
      .then(res => this.mensageSTT(res.data));
    // axios.post('http://192.168.42.89:2931/chat/send_message', speak)
    //   .then(res => console.warn(res.data));
  }

  mensageSTT = function(mes){
    //   console.warn(mes.speechs);
      this.playSound(mes.speechs);
      this.onSend(this.userMenss(mes.messages[0]), false);
      this.onSend(this.bot(mes.messages), false)
  }

  bot = function(resMesages){
    this.messages = null;
    this.messages = [
      {
        _id:  Math.round(Math.random() * 1000000),
        text: resMesages[1],
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'BaBi',
          avatar: 'https://tsume-art.com/storage/app/uploads/public/82b/436/eac/thumb__1440x0_0_0_crop.jpg',
        },
      },
    ];

    return this.messages;
  }

  userMenss = function(resMesages){
    this.messages = null;
    this.messages = [
      {
        _id:  Math.round(Math.random() * 1000000),
        text: 'Você disse: ' + resMesages,
        user: {
          _id: 1,
        },
      },
    ];

    return this.messages;
  }

  componentDidMount() {
    AudioRecorder.requestAuthorization().then((isAuthorised) => {
      this.setState({ hasPermission: isAuthorised });

      if (!isAuthorised) return;

      this.prepareRecordingPath(this.state.audioPath);

      AudioRecorder.onProgress = (data) => {
        this.setState({currentTime: Math.floor(data.currentTime)});
      };

      AudioRecorder.onFinished = (data) => {
        // Android callback comes in the form of a promise instead.
        if (Platform.OS === 'ios') {
          this._finishRecording(data.status === "OK", data.audioFileURL, data.audioFileSize);
        }
      };
    });
  }

  renderLoading() {
    if (!this.state.messages.length && !this.state.fetchChats) {
        return (
            <View style={{ marginTop: 100 }}>
                <ActivityIndicator color="black" animating size="large" />
            </View>
        );
    }
  }

  renderAndroidMicrophone() {
    if (Platform.OS === "android") {
        return (
            <Ionicons
                name="ios-mic"
                size={35}
                hitSlop={{ top: 20, bottom: 20, left: 50, right: 50 }}
                color={this.state.startAudio ? "red" : "black"}
                style={{
                    bottom: 50,
                    right: Dimensions.get("window").width / 2,
                    position: "absolute",
                    shadowColor: "#000",
                    shadowOffset: { width: 0, height: 0 },
                    shadowOpacity: 0.5,
                    zIndex: 2,
                    backgroundColor: "transparent"
                }}
                onPress={this.handleAudio}
            />
        );
    }
  }

  handleAudio = async () => {
    if (!this.state.startAudio) {
        this.setState({
            startAudio: true
        });
        if(!this.state.startAudio){
          this.prepareRecordingPath(this.state.audioPath);
        }
        await AudioRecorder.startRecording()
    } else {
        this.setState({ startAudio: false });
        await AudioRecorder.stopRecording();
        AudioRecorder.onFinished = (data) => {
            this.audioBot(data.base64)
        };
    }
  };

  render() {
    return (
        <View style={{ flex: 1 }}>
        <NavigationBar
            title={{ title: "Banco do Brasil - BaBi" }}
        />
        {this.renderLoading()}
        {this.renderAndroidMicrophone()}
        <GiftedChat
            messages={this.state.messages}
            onSend={messages => this.onSend(messages)}
            alwaysShowSend
            showUserAvatar
            isAnimated
            showAvatarForEveryMessage
            renderBubble={this.renderBubble}
            messageIdGenerator={this.messageIdGenerator}
            onPressAvatar={this.handleAvatarPress}
            renderActions={() => {
                if (Platform.OS === "ios") {
                    return (
                        <Ionicons
                            name="ios-mic"
                            size={35}
                            hitSlop={{ top: 20, bottom: 20, left: 50, right: 50 }}
                            color={this.state.startAudio ? "red" : "black"}
                            style={{
                                bottom: 50,
                                right: Dimensions.get("window").width / 2,
                                position: "absolute",
                                shadowColor: "#000",
                                shadowOffset: { width: 0, height: 0 },
                                shadowOpacity: 0.5,
                                zIndex: 2,
                                backgroundColor: "transparent"
                            }}
                            onPress={this.handleAudio}
                        />
                    );
                }
            }}
        />
        <KeyboardAvoidingView />
    </View>
    )
  }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: "#2b608a",
      },
      controls: {
        justifyContent: 'center',
        alignItems: 'center',
        flex: 1,
      },
      progressText: {
        paddingTop: 50,
        fontSize: 50,
        color: "#fff"
      },
      button: {
        padding: 20
      },
      disabledButtonText: {
        color: '#eee'
      },
      buttonText: {
        fontSize: 20,
        color: "#fff"
      },
      activeButtonText: {
        fontSize: 20,
        color: "#B81F00"
      }
  });