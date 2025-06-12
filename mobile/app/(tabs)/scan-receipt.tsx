import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import Colors from '@/constants/Colors';
import Button from '@/components/ui/Button';
import { Camera, CameraIcon, ImageIcon, ArrowLeft, ZapIcon } from 'lucide-react-native';

export default function ScanReceiptScreen() {
  const [type, setType] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [scanning, setScanning] = useState(false);

  if (!permission) {
    // Camera permissions are still loading
    return null;
  }

  if (!permission.granted) {
    // Camera permissions not granted
    return (
      <SafeAreaView style={styles.permissionContainer}>
        <Text style={styles.permissionTitle}>Camera Access Required</Text>
        <Text style={styles.permissionText}>
          We need camera access to scan your receipts and automatically add items to your pantry.
        </Text>
        <Button 
          title="Grant Permission" 
          onPress={requestPermission} 
          style={styles.permissionButton}
        />
        <Button 
          title="Go Back" 
          onPress={() => router.back()} 
          variant="outline" 
          style={{ marginTop: 12 }}
        />
      </SafeAreaView>
    );
  }

  const toggleCameraType = () => {
    setType(current => (current === 'back' ? 'front' : 'back'));
  };

  const handleScan = () => {
    // In a real app, this would process the receipt with AI
    setScanning(true);
    
    // Simulate scanning delay
    setTimeout(() => {
      setScanning(false);
      
      // Show success alert and navigate back
      alert('Receipt scanned successfully! 5 new items added to your pantry.');
      router.back();
    }, 2000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <ArrowLeft size={24} color="white" />
        </TouchableOpacity>
        <Text style={styles.title}>Scan Receipt</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.cameraContainer}>
        <CameraView
          style={styles.camera}
        >
          {/* Camera Overlay */}
          <View style={styles.overlay}>
            <View style={styles.scanArea}>
              {scanning && (
                <View style={styles.scanningIndicator}>
                  <ZapIcon size={24} color={Colors.primary[500]} />
                  <Text style={styles.scanningText}>Scanning...</Text>
                </View>
              )}
            </View>
          </View>
          
          <View style={styles.controls}>
            <TouchableOpacity 
              style={styles.flipButton} 
              onPress={toggleCameraType}
            >
              <CameraIcon size={24} color="white" />
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.captureButton}
              onPress={handleScan}
              disabled={scanning}
            >
              <View style={[styles.captureInner, scanning && { opacity: 0.7 }]}>
                <Camera size={28} color={Colors.primary[500]} />
              </View>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.galleryButton}
              onPress={() => alert('Photo library access will be available in a future update.')}
            >
              <ImageIcon size={24} color="white" />
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
      
      <View style={styles.instructions}>
        <Text style={styles.instructionsTitle}>How to Scan:</Text>
        <Text style={styles.instructionsText}>
          1. Place your receipt on a flat surface with good lighting
        </Text>
        <Text style={styles.instructionsText}>
          2. Ensure the entire receipt is visible in the frame
        </Text>
        <Text style={styles.instructionsText}>
          3. Tap the capture button to scan
        </Text>
        <Text style={styles.instructionsNote}>
          We'll automatically identify grocery items and add them to your pantry!
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  title: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: 'white',
  },
  cameraContainer: {
    flex: 1,
    overflow: 'hidden',
  },
  camera: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: 280,
    height: 400,
    borderWidth: 2,
    borderColor: 'white',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  scanningIndicator: {
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  scanningText: {
    fontFamily: 'Inter-SemiBold',
    color: Colors.primary[500],
    marginLeft: 8,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 20,
    paddingHorizontal: 30,
  },
  flipButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 30,
  },
  captureInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    backgroundColor: 'white',
  },
  permissionTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 22,
    color: Colors.neutral[800],
    marginBottom: 16,
    textAlign: 'center',
  },
  permissionText: {
    fontFamily: 'Inter-Regular',
    fontSize: 16,
    color: Colors.neutral[600],
    marginBottom: 32,
    textAlign: 'center',
    lineHeight: 24,
  },
  permissionButton: {
    minWidth: 200,
  },
  instructions: {
    backgroundColor: 'black',
    padding: 20,
  },
  instructionsTitle: {
    fontFamily: 'Poppins-SemiBold',
    fontSize: 18,
    color: 'white',
    marginBottom: 12,
  },
  instructionsText: {
    fontFamily: 'Inter-Regular',
    fontSize: 14,
    color: Colors.neutral[300],
    marginBottom: 6,
    paddingLeft: 12,
  },
  instructionsNote: {
    fontFamily: 'Inter-Medium',
    fontSize: 14,
    color: Colors.primary[300],
    marginTop: 12,
    textAlign: 'center',
  },
});