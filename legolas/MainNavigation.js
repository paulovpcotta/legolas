import Login from './src/Login';
import Photo from './src/pages/Photo';
import Voices from './src/pages/Voices';
import { createStackNavigator, createAppContainer } from 'react-navigation';

const screens = {
    Login: {
    screen: Login
    },
  Photo: {
    screen: Photo
  },
  Voices: {
    screen: Voices
  }
}

const config = {
  headerMode: 'none',
  initialRouteName: 'Login'
}

const MainNavigator = createStackNavigator(screens,config);
export default createAppContainer(MainNavigator);