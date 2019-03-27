import React, { Component } from 'react';
import {
    AppRegistry,
    Dimensions,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
    Alert
  } from 'react-native';

import { RNCamera } from 'react-native-camera';
import axios from 'axios';

export default class Photo extends Component {

    takePicture = async function() {
        if (this.camera) {
          const options = { quality: 0.5, base64: true, fixOrientation: true, forceUpOrientation: true, orientation: 'portrait'};
          const data = await this.camera.takePictureAsync(options);
          const rec = {
            base64: data.base64
          }
          axios.post('http://40.114.36.222:2931/api/detection_recognition', rec)
            .then(res => this.login(res)).catch(error => {
              Alert.alert('Favor tentar novamente!')
          });;
          //Alert.alert(data.uri);
        }
      }

      login = function(res){
        if(res.data.predict == null){
            Alert.alert('Favor tentar novamente!');
        }else if(res.data.predict != null && res.data.predict[0].name != 'unknown' && res.data.predict[0].name != ''){
            this.props.navigation.navigate('Voices', {name: res.data.predict[0].name});
        }else if(res.data.predict[0].name == 'unknown' && res.data.predict[0].name == ''){
            Alert.alert('Favor tentar novamente!');
        }
      }
        
      render() {
        return (
          <View style={styles.container}>
            <RNCamera
                ref={ref => {
                  this.camera = ref;
                }}
                style = {styles.preview}
                type={RNCamera.Constants.Type.front}
                autoFocus={RNCamera.Constants.AutoFocus.on}
                flashMode={RNCamera.Constants.FlashMode.off}
                permissionDialogTitle={'Permissão para usar a câmera'}
                permissionDialogMessage={'We need your permission to use your camera phone'}
            />
            <View style={{flex: 0, flexDirection: 'row', justifyContent: 'center',}}>
            <TouchableOpacity
                onPress={this.takePicture.bind(this)}
                style = {styles.capture}
           >
                <Text style={{fontSize: 14}}> Entrar </Text>
            </TouchableOpacity>
            </View>
          </View>
        );
      }
}


const styles = StyleSheet.create({
    container: {
      flex: 1,
      flexDirection: 'column',
      backgroundColor: 'black'
    },
    preview: {
      flex: 1,
      justifyContent: 'flex-end',
      alignItems: 'center'
    },
    capture: {
      flex: 0,
      backgroundColor: '#fff',
      borderRadius: 5,
      padding: 15,
      paddingHorizontal: 20,
      alignSelf: 'center',
      margin: 20
    }
  });