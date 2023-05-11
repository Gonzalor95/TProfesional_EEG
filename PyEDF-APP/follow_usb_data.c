
// The one triggered by Interruption
static uint8_t USBD_CDC_DataOut(USBD_HandleTypeDef *pdev, uint8_t epnum)
{
  USBD_CDC_HandleTypeDef *hcdc = (USBD_CDC_HandleTypeDef *)pdev->pClassDataCmsit[pdev->classId];

  if (pdev->pClassDataCmsit[pdev->classId] == NULL)
  {
    return (uint8_t)USBD_FAIL;
  }

  /* Get the received data length */
  hcdc->RxLength = USBD_LL_GetRxDataSize(pdev, epnum);

  /* USB data will be immediately processed, this allow next USB traffic being
  NAKed till the end of the application Xfer */

  ((USBD_CDC_ItfTypeDef *)pdev->pUserData[pdev->classId])->Receive(hcdc->RxBuffer, &hcdc->RxLength); // --> 

  return (uint8_t)USBD_OK;
}

static int8_t CDC_Receive_FS(uint8_t* Buf, uint32_t *Len)
{
  /* USER CODE BEGIN 6 */

  USBD_CDC_SetRxBuffer(&hUsbDeviceFS, &Buf[0]);
  USBD_CDC_ReceivePacket(&hUsbDeviceFS);
  //// The rest...

}

uint8_t USBD_CDC_ReceivePacket(USBD_HandleTypeDef *pdev){
    (void)USBD_LL_PrepareReceive(pdev, CDCOutEpAdd, hcdc->RxBuffer,
                                 CDC_DATA_FS_OUT_PACKET_SIZE);
}

USBD_StatusTypeDef USBD_LL_PrepareReceive(USBD_HandleTypeDef *pdev, uint8_t ep_addr, uint8_t *pbuf, uint32_t size)
{
  HAL_StatusTypeDef hal_status = HAL_OK;
  USBD_StatusTypeDef usb_status = USBD_OK;

  hal_status = HAL_PCD_EP_Receive(pdev->pData, ep_addr, pbuf, size);

  usb_status =  USBD_Get_USB_Status(hal_status); // Can get HAL_OK, HAL_BUSY, HAL_TIMEOUT(error) or HAL_ERROR

  return usb_status;
}
