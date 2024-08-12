import contextlib
import hid
import usbmonitor
import threading

supportedDevices = {
    # (Vendor ID, Product ID):{(Usage Page, Usage ID): (Device Type, Report Length)}
    (0x4B50,0xEF8D): {(0xFF60, 0x61): ("kbd-60-rgbmat", 32)}
}

@contextlib.contextmanager
def maintainBus():
    mutex = threading.Lock()
    connectedDevices = {}
    for (vidpid, usageSupport) in supportedDevices.items():
        for (usage, (deviceType, reportLength)) in usageSupport.items():
            connectedDevices[deviceType] = {}

    monitor = usbmonitor.USBMonitor(filter_devices=tuple({
        usbmonitor.attributes.ID_VENDOR_ID:str(vid),
        usbmonitor.attributes.ID_MODEL_ID:str(pid)
    } for (vid, pid) in supportedDevices.keys()))

    # Must be idempotent because the monitor thread races with get_available_devices during startup
    def onConnect(did, dinfo):
        vidpid = (int(dinfo['ID_VENDOR_ID']), int(dinfo['ID_MODEL_ID']))
        with mutex:
            print('USB device with vid=0x%04x pid=0x%04x id=%s has been connected' % (*vidpid, did))

            for (dtype, didToHidDevRL) in connectedDevices.items():
                if did in didToHidDevRL.keys():
                    print('USB device with id=%s is already connected' % did)
                    return

            allHidIntfs = hid.enumerate(*vidpid)
            usageSupport = supportedDevices[*vidpid]
            for hidIntf in allHidIntfs:
                usage = (hidIntf['usage_page'], hidIntf['usage'])
                if usage not in usageSupport.keys():
                    #print('USB device with vid=0x%04x pid=0x%04x id=%s has unknown usage page=0x%04x id=0x%04x' % (*vidpid, did, *usage))
                    continue
                
                deviceType, reportLength = usageSupport[usage]
                connectedDevices[deviceType][did] = (hidIntf['path'], reportLength)
                print('USB device with vid=0x%04x pid=0x%04x id=%s has known usage page=0x%04x id=0x%04x REGISTERED AS %s w/ rlen=%d' % (*vidpid, did, *usage, deviceType, reportLength))

    # Must be idempotent because the monitor thread races with get_available_devices during startup
    def onDisconnect(did, dinfo):
        with mutex:
            print('USB device with id=%s has been disconnected' % did)
            for (deviceType, didToHidDevRL) in connectedDevices.items():
                if did in didToHidDevRL:
                    (hidDevice, rl) = didToHidDevRL[did]
                    del didToHidDevRL[did]
                    print('USB device with id=%s has been UNREGISTERED as %s w/ rlen=%d' % (did, deviceType, rl))

    try:
        print('Starting USB Monitor...')
        monitor.start_monitoring(on_connect=onConnect, on_disconnect=onDisconnect)

        print('USB Monitor is running. Checking if any devices are already present...')
        with mutex:
            initialDevices = monitor.get_available_devices()

        found = False
        for (did,dinfo) in initialDevices.items():
            found = True
            onConnect(did, dinfo)
        print('Already-present devices were ' + ('' if found else 'not ') + 'found')

        def sendMsg(deviceType, body):
            for (intfPath, reportLength) in connectedDevices['kbd-60-rgbmat'].values():
                report = [0x00] * (reportLength + 1) # First byte is Report ID
                report[1:len(body) + 1] = body

                #print("Report:", report)
                #print(report)

                try:
                    intf = hid.Device(path=intfPath)
                    intf.write(bytes(report))

                #respReport = intf.read(reportLength, timeout=1)
                #print("Response:", respReport)
                finally:
                    intf.close()

        yield sendMsg

    finally:
        print('Stopping USB Monitor...')
        monitor.stop_monitoring()
        print('USB Monitor has stopped')

