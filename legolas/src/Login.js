import React, { Component } from 'react';
import {
    ScrollView,
    Text,
    TextInput,
    View,
    Button,
    StyleSheet,
    Alert
} from 'react-native';

export default class Login extends Component {
    constructor(props) {
        super(props);
        
        this.state = {
            username: '',
            password: '',
        };
    }
    
    onLogin() {
        const { username, password } = this.state;
        this.props.navigation.navigate('Photo');
    }

    render() {
        return (
            <View style={styles.container}>
                <ScrollView style={{padding: 20}}>
                <Text 
                    style={{fontSize: 27}}>
                    Login
                </Text>
                <TextInput placeholder='Login' style={styles.input}
                value={this.state.username}
                onChangeText={(username) => this.setState({ username })}/>
                <TextInput placeholder='Senha' style={styles.input}
                value={this.state.password}
                onChangeText={(password) => this.setState({ password })}
                password={true} secureTextEntry/>
                <View style={{margin:7}} />
                <Button 
                          onPress={this.onLogin.bind(this)}
                          title="Entrar"
                          style={styles.button}
                      />
                  </ScrollView>
            </View>
            )
    }
}

const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#ecf0f1',
    },
    button: {
      width: 200,
      height: 44,
      top: 40,
      padding: 10,
      borderWidth: 1,
      borderColor: 'black',
      marginBottom: 10,
    },
    input: {
        width: 200,
        height: 44,
        padding: 10,
        borderBottomColor: 'black',
        marginBottom: 10,
      },
});